#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regicide Game - Main Launcher
Regicide弑君者游戏 - 主启动器
"""

def main():
    print("🃏 Regicide - 弑君者桌游")
    print("=" * 40)
    print()
    print("启动最新版本游戏...")
    
    # Check dependencies
    try:
        import pygame
        print(f"✅ Pygame {pygame.version.ver} 已就绪")
    except ImportError:
        print("❌ 错误：未安装Pygame")
        print("请运行：pip install pygame")
        input("按Enter键退出...")
        return
    
    try:
        from regicide_fixed import RegicideFixedGUI
        print("🎮 正在启动游戏...")
        game = RegicideFixedGUI()
        game.run()
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断游戏")
    except Exception as e:
        print(f"❌ 游戏错误：{e}")
        print("请检查所有文件是否完整")
    finally:
        print("🎊 感谢游玩！")

if __name__ == "__main__":
    main()