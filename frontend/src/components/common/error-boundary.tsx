/**
 * Error boundary component.
 * Catches React rendering errors and displays a recovery UI.
 */

import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error("[ErrorBoundary]", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex h-full min-h-[400px] flex-col items-center justify-center gap-6 p-8">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-danger/10 text-danger">
            <AlertTriangle className="h-8 w-8" />
          </div>
          <div className="flex flex-col items-center gap-2 text-center">
            <h2 className="text-xl font-semibold text-text">
              Something went wrong
            </h2>
            <p className="max-w-md text-sm text-muted">
              An unexpected error occurred. Please try again or contact support
              if the problem persists.
            </p>
            {this.state.error && (
              <code className="mt-2 max-w-lg rounded-lg bg-white/[0.04] px-4 py-2 text-xs text-muted">
                {this.state.error.message}
              </code>
            )}
          </div>
          <button
            onClick={this.handleReset}
            className="flex items-center gap-2 rounded-lg bg-white/[0.06] px-4 py-2.5 text-sm font-medium text-text transition-colors hover:bg-white/[0.1]"
          >
            <RefreshCw className="h-4 w-4" />
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
