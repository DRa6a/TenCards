"""
models.py - 游戏核心数据模型
包含：卡牌、玩家、牌堆、游戏状态、神兽
"""
import random
from enum import Enum
from typing import List, Optional

# ==========================================
# 基础枚举与类
# ==========================================

class CardXiang(Enum):
    """牌相：天、地、人、道"""
    TIAN = "天"
    DI = "地"
    REN = "人"
    DAO = "道"

class XiaoZi:
    """小字（牌面数字）"""
    def __init__(self, value: int):
        if not 1 <= value <= 12:
            raise ValueError("小字必须在1-12之间")
        self.value = value

    def __repr__(self):
        return str(self.value)

class Card:
    """卡牌类"""
    def __init__(self, xiang: CardXiang, xiao_zi: XiaoZi):
        self.xiang = xiang
        self.xiao_zi = xiao_zi

    @property
    def name(self) -> str:
        """卡牌名称，如：天1、道3"""
        return f"{self.xiang.value}{self.xiao_zi.value}"

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

class DivineBeast(Enum):
    """神兽枚举"""
    QING_LONG = "青龙"
    BAI_HU = "白虎"
    ZHU_QUE = "朱雀"
    XUAN_WU = "玄武"
    QILIN = "麒麟"
    FENG_HUANG = "凤凰"

# ==========================================
# 牌堆类
# ==========================================

class Deck:
    """牌堆管理类"""
    def __init__(self):
        self.cards: List[Card] = []
        self._init_standard_deck()

    def _init_standard_deck(self):
        """初始化标准42张牌"""
        self.cards.clear()
        # 天地人各12张
        for xiang in [CardXiang.TIAN, CardXiang.DI, CardXiang.REN]:
            for i in range(1, 13):
                self.cards.append(Card(xiang, XiaoZi(i)))
        # 道牌6张
        for i in range(1, 7):
            self.cards.append(Card(CardXiang.DAO, XiaoZi(i)))

    def shuffle(self):
        """洗牌"""
        random.shuffle(self.cards)
        print(f"牌堆已洗牌，当前剩余 {len(self.cards)} 张")

    def draw(self, count: int = 1) -> List[Card]:
        """抽牌"""
        drawn = []
        for _ in range(count):
            if self.cards:
                drawn.append(self.cards.pop())
        return drawn

    def __len__(self):
        return len(self.cards)

# ==========================================
# 玩家类
# ==========================================

class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand: List[Card] = []
        self.played_cards: List[Card] = [] # 本回合已打出的牌
        self.alive = True
        # 初始化神兽池
        self.available_beasts = list(DivineBeast)

    def draw_cards(self, deck: Deck, count: int = 6) -> None:
        """从指定牌堆摸牌"""
        drawn = deck.draw(count)
        self.hand.extend(drawn)

    def has_cards(self) -> bool:
        return len(self.hand) > 0

    def show_hand(self) -> str:
        return ", ".join([str(c) for c in self.hand])

    def get_card_by_name(self, name: str) -> Optional[Card]:
        """根据名称获取手牌"""
        for card in self.hand:
            if card.name == name:
                return card
        return None

    def play_card(self, card: Card) -> None:
        """打出一张牌"""
        if card in self.hand:
            self.hand.remove(card)
            self.played_cards.append(card)
            print(f"{self.name} 打出了 {card}")
        else:
            print(f"错误：{self.name} 手中无此牌")

# ==========================================
# 游戏状态类
# ==========================================

class GameState:
    def __init__(self):
        self.players: List[Player] = []
        self.deck: Optional[Deck] = None # 初始为空，每回合重新生成
        self.current_round = 0
        self.current_player_index = 0
        self.true_xiang: Optional[CardXiang] = None
        self.current_phase = "准备阶段"
        self.challenge_result = None # 存储质疑结果

    def get_alive_players(self) -> List[Player]:
        return [p for p in self.players if p.alive]

    def get_current_player(self) -> Player:
        # 简单的索引获取，假设调用前已确保玩家存活
        return self.players[self.current_player_index]

    def next_player(self):
        """切换到下一个存活玩家"""
        if not self.get_alive_players():
            return

        # 找到下一个存活者
        start_index = self.current_player_index
        while True:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            if self.players[self.current_player_index].alive:
                break
            # 防止死循环（如果只剩一人或无人）
            if self.current_player_index == start_index:
                break

    def determine_true_xiang(self):
        """随机确定本回合真牌牌相"""
        self.true_xiang = random.choice([CardXiang.TIAN, CardXiang.DI, CardXiang.REN])
        print(f"本回合真牌牌相确定为: {self.true_xiang.value}")

    def resolve_challenge(self, challenger: Player, defender: Player):
        """
        处理质疑逻辑
        返回结果存入 self.challenge_result
        """
        print(f"\n>>> 质疑判定 <<<")
        print(f"质疑者: {challenger.name} vs 出牌者: {defender.name}")

        # 获取最后打出的牌
        if not defender.played_cards:
            print("错误：出牌者没有出牌记录。")
            self.challenge_result = None
            return

        last_card = defender.played_cards[-1]
        print(f"翻开出牌者的牌: {last_card}")

        # 判定胜负
        # 规则：
        # 1. 如果出的牌是"道牌" -> 出牌者赢 (质疑失败)
        # 2. 如果出的牌与"真牌牌相"不同 -> 出牌者赢 (质疑失败，因为他说的是真话)
        # 3. 如果出的牌与"真牌牌相"相同 -> 质疑者赢 (质疑成功)

        challenger_win = False

        if last_card.xiang == CardXiang.DAO:
            print("判定：出牌为【道牌】，质疑无效！")
            challenger_win = False
        elif last_card.xiang != self.true_xiang:
            print(f"判定：牌相({last_card.xiang.value}) != 真牌({self.true_xiang.value})，出牌者说真话，质疑失败！")
            challenger_win = False
        else:
            print(f"判定：牌相({last_card.xiang.value}) == 真牌({self.true_xiang.value})，出牌者说谎(或被迫)，质疑成功！")
            challenger_win = True

        self.challenge_result = {
            "challenger": challenger,
            "defender": defender,
            "card": last_card,
            "challenger_win": challenger_win
        }

    def execute_life_death(self):
        """执行生死判决（神兽对决）"""
        if not self.challenge_result:
            return

        challenger = self.challenge_result['challenger']
        defender = self.challenge_result['defender']
        challenger_win = self.challenge_result['challenger_win']

        # 简化版神兽对决：随机抽取神兽比较大小
        # 胜者存活，败者死亡
        print("\n--- 神兽对决 ---")

        # 双方选择神兽 (这里简化为随机选择，后续可扩展为玩家选择)
        # 移除已使用的神兽逻辑暂略，直接随机

        c_beast = random.choice(list(DivineBeast))
        d_beast = random.choice(list(DivineBeast))

        print(f"{challenger.name} 召唤了 [{c_beast.value}]")
        print(f"{defender.name} 召唤了 [{d_beast.value}]")

        # 决定谁死
        # 如果质疑成功 -> 出牌者死
        # 如果质疑失败 -> 质疑者死

        loser = None
        if challenger_win:
            loser = defender
        else:
            loser = challenger

        loser.alive = False
        print(f"\n!!! {loser.name} 在神兽对决中落败，确认死亡 !!!")

        # 清空结果
        self.challenge_result = None

    def check_game_end(self) -> bool:
        """检查游戏是否结束 (返回False表示结束)"""
        alive_count = len(self.get_alive_players())
        return alive_count > 1
