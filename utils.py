"""
utils.py - 游戏工具函数
包含：输入处理、显示美化等
"""
from typing import List

# ==========================================
# 输入输出工具
# ==========================================

def get_valid_input(prompt: str, valid_options: List[str] = None) -> str:
    """获取有效的用户输入"""
    while True:
        try:
            user_input = input(prompt).strip()
            if valid_options:
                if user_input in valid_options:
                    return user_input
                else:
                    print(f"无效输入，请输入: {', '.join(valid_options)}")
            else:
                return user_input
        except KeyboardInterrupt:
            print("\n游戏被中断")
            exit(0)
        except Exception as e:
            print(f"输入错误: {e}")

def print_separator(char: str = "=", length: int = 50):
    """打印分隔线"""
    print(char * length)

def print_game_info(game_state):
    """打印游戏状态信息"""
    print_separator()
    print(f"回合: {game_state.current_round}")
    print(f"阶段: {game_state.current_phase}")
    if game_state.true_xiang:
        print(f"真牌牌相: {game_state.true_xiang.value}")
    else:
        print("真牌牌相: 未确定")
    print_separator()

    # 显示玩家状态
    for player in game_state.players:
        status = "✓ 存活" if player.alive else "✗ 死亡"
        beast_info = f"神兽池: {len(player.available_beasts)}/6"
        print(f"{player.name}: {status} | 手牌: {len(player.hand)}张 | {beast_info}")

    print_separator()
