#!/usr/bin/env python3
"""
Initialize SQLite database schema and seed candidates from candidates.jsonl.

Usage:
    python scripts/init_db.py --candidates datasets/candidates.jsonl
"""

import argparse
import time
import sys
from pathlib import Path
from loguru import logger

# Add backend directory to Python path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.shared.database import get_db_path
from app.modules.candidates.repository import CandidateRepository
from app.modules.candidates.service import CandidateService

def parse_args():
    parser = argparse.ArgumentParser(description="Initialize database and seed candidates.")
    parser.add_argument(
        "--candidates",
        type=str,
        default="datasets/candidates.jsonl",
        help="Path to candidates.jsonl (or candidates.jsonl.gz)"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    candidates_path = Path(args.candidates)
    
    # Check if the candidates file exists
    if not candidates_path.exists():
        # Let's check common downloads location as fallback
        fallback = Path(r"C:\Users\ANKIT PARIDA\Downloads\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl")
        if fallback.exists():
            logger.info("Provided candidates path not found. Found file at fallback: {path}", path=fallback)
            candidates_path = fallback
        else:
            logger.error("Candidates file not found at '{path}' or fallback.", path=candidates_path)
            sys.exit(1)
            
    logger.info("Initializing database at: {db}", db=get_db_path())
    start_time = time.time()
    
    # Create tables
    CandidateRepository.create_tables()
    
    logger.info("Streaming and seeding candidates from: {file}", file=candidates_path)
    
    batch = []
    batch_size = 1000
    total_processed = 0
    valid_count = 0
    malformed_count = 0
    honeypot_count = 0
    
    # Set up custom logging config for clean CLI output
    logger.remove()
    logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}", level="INFO")
    
    try:
        lines_iterator = CandidateService.stream_load_jsonl(candidates_path)
        
        for line_num, line in enumerate(lines_iterator):
            total_processed += 1
            try:
                data = json.loads(line)
            except Exception as json_err:
                malformed_count += 1
                logger.warning(
                    "Malformed JSON at line {line}: {err}",
                    line=line_num + 1,
                    err=str(json_err)
                )
                # Store malformed entry log in db
                malformed_record = {
                    "candidate_id": f"MALFORMED_LINE_{line_num + 1}",
                    "is_valid": 0,
                    "is_honeypot": 0,
                    "validation_error": f"JSON decoding error: {str(json_err)}",
                    "raw_json": line
                }
                batch.append(malformed_record)
                if len(batch) >= batch_size:
                    CandidateRepository.insert_candidates_batch(batch)
                    batch = []
                continue
                
            # Validate record
            is_valid, err_msg, candidate = CandidateService.validate_record(data)
            
            if not is_valid:
                malformed_count += 1
                candidate_id = data.get("candidate_id", f"MALFORMED_RECORD_{line_num + 1}")
                malformed_record = {
                    "candidate_id": candidate_id,
                    "is_valid": 0,
                    "is_honeypot": 0,
                    "validation_error": err_msg,
                    "raw_json": json.dumps(data)
                }
                batch.append(malformed_record)
            else:
                # Valid: extract features
                valid_count += 1
                features = CandidateService.extract_features(candidate)
                if features["is_honeypot"]:
                    honeypot_count += 1
                batch.append(features)
                
            # Batch insert
            if len(batch) >= batch_size:
                CandidateRepository.insert_candidates_batch(batch)
                batch = []
                
            if total_processed % 10000 == 0:
                elapsed = time.time() - start_time
                logger.info(
                    "Processed {total:,} records... ({valid:,} valid, {malformed:,} malformed, {honeypots:,} honeypots) | Elapsed: {elapsed:.1f}s",
                    total=total_processed,
                    valid=valid_count,
                    malformed=malformed_count,
                    honeypots=honeypot_count,
                    elapsed=elapsed
                )
                
        # Insert remaining records
        if batch:
            CandidateRepository.insert_candidates_batch(batch)
            
    except Exception as e:
        logger.exception("Error processing candidate dataset: {err}", err=str(e))
        sys.exit(1)
        
    duration = time.time() - start_time
    logger.info("Dataset loaded. Total: {total:,} | Valid: {valid:,} | Malformed: {malformed:,} | Honeypots: {honeypots:,}",
                total=total_processed, valid=valid_count, malformed=malformed_count, honeypots=honeypot_count)
    
    # Calculate statistics and cache them
    logger.info("Computing global dataset statistics...")
    stats = CandidateService.calculate_global_statistics()
    CandidateRepository.save_statistics(stats)
    logger.info("Statistics saved to database cache.")
    
    logger.info("Database seeding finished in {duration:.1f}s.", duration=duration)
    
    # Print summary
    print("\n" + "="*50)
    print("DATABASE SEEDING SUMMARY")
    print("="*50)
    print(f"Total Profiles Processed: {total_processed:,}")
    print(f"Valid Profiles:           {valid_count:,}")
    print(f"Malformed Profiles:       {malformed_count:,}")
    print(f"Honeypot Profiles:        {honeypot_count:,}")
    print(f"Honeypot Rate:            {honeypot_count / max(1, valid_count) * 100:.2f}%")
    print(f"Time Taken:               {duration:.2f}s")
    print("="*50 + "\n")

if __name__ == "__main__":
    import json
    main()
