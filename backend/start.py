#!/usr/bin/env python3
"""
Startup script for AI Image Editor Backend
"""
import os
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description="AI Image Editor Backend")
    parser.add_argument(
        "--host",
        default=os.getenv("HOST", "0.0.0.0"),
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "8000")),
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes"
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("LOG_LEVEL", "info"),
        choices=["debug", "info", "warning", "error", "critical"],
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Import uvicorn here to avoid early import issues
    import uvicorn
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║              AI Image Editor - Backend                    ║
╠═══════════════════════════════════════════════════════════╣
║  Host:      {args.host:<45} ║
║  Port:      {args.port:<45} ║
║  Reload:    {str(args.reload):<45} ║
║  Workers:   {args.workers:<45} ║
║  Log Level: {args.log_level:<45} ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,
        log_level=args.log_level,
        access_log=True
    )


if __name__ == "__main__":
    main()
