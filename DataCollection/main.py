#!/usr/bin/env python3
"""
PostureBuddy - Posture Detection and Monitoring System

Main entry point for the application.
"""

from utils.config import ArgumentParser
from utils.app import PostureBuddyApp


def main():
    """Main entry point"""
    # Parse command line arguments
    arg_parser = ArgumentParser()
    args = arg_parser.parse()

    # Create and run the application
    app = PostureBuddyApp(args)
    app.run()


if __name__ == "__main__":
    main()
