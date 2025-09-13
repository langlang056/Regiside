#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regicide Game - Simple Launcher
"""

import sys
import os

def main():
    print("Regicide - Card Battle Game")
    print("=" * 40)
    print()
    print("Game Features:")
    print("- Complete Regicide rules")
    print("- Beautiful graphics")
    print("- 12 enemies to defeat")
    print("- Suit abilities system")
    print("- Combo card mechanics")
    print()
    
    # Check dependencies
    try:
        import pygame
        print(f"Pygame {pygame.version.ver} ready!")
    except ImportError:
        print("Error: Pygame not installed")
        print("Please run: pip install pygame")
        input("Press Enter to exit...")
        return
    
    print("Starting game...")
    
    try:
        from regicide_fixed import RegicideFixedGUI
        game = RegicideFixedGUI()
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Game error: {e}")
        print("Please check if all files are complete")
    finally:
        print("Thanks for playing!")

if __name__ == "__main__":
    main()