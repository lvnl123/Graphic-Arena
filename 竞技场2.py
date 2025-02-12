import random
import time
import pygame
import math
import numpy as np
from abc import ABC, abstractmethod

# ---------- 原始代码部分（完全未修改） ----------
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("图形竞技场")

# 颜色定义
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# 字体设置
chinese_font = pygame.font.SysFont("SimHei", 24)
emoji_font = pygame.font.SysFont("Segoe UI Emoji", 24)


class Shape(ABC):
    def __init__(self, name, health, attack_damage, color, x, y, team=None):
        self.name = name
        self.health = health
        self.attack_damage = attack_damage
        self.color = color
        self.x = x
        self.y = y
        self.is_alive = True
        self.level = 1
        self.team = team
        self.target_x = None
        self.target_y = None
        self.speed = 2
        self.is_moving = False
        self.attack_cooldown = 0
        self.exp = 0
        self.exp_to_next_level = 100
        self.skill_cooldowns = {
            "range_attack": 0,
            "heal": 0,
            "teleport": 0,
            "ultimate": 0
        }

    def level_up(self):
        """升级逻辑"""
        self.level += 1
        self.health += 20
        self.attack_damage += 3
        self.exp -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        print(f"{self.name} 升级了！当前等级：Lv{self.level}")
        # 检查是否需要升阶
        if self.level == 2:  # 假设等级达到 3 时升阶
            self.evolve()

    def evolve(self):
        """升阶逻辑（子类需实现）"""
        pass

    @abstractmethod
    def special_ability(self, base_damage, target):
        """每个图形特有的能力"""
        pass

    def attack(self, target):
        if self.attack_cooldown > 0:
            return 0
        base_damage = self.attack_damage + random.randint(-2, 2)
        # 克制倍率
        damage_multiplier = self.get_damage_multiplier(target)
        final_damage = int(base_damage * damage_multiplier)
        final_damage = self.special_ability(final_damage, target)
        target.take_damage(final_damage)
        self.attack_cooldown = 60
        return final_damage

    def get_damage_multiplier(self, target):
        """根据克制关系计算伤害倍率"""
        if isinstance(self, Circle) and isinstance(target, Triangle):
            return 1.5  # 圆形克制三角形
        elif isinstance(self, Triangle) and isinstance(target, Square):
            return 1.5  # 三角形克制方形
        elif isinstance(self, Square) and isinstance(target, Hexagon):
            return 1.5  # 方形克制六边形
        elif isinstance(self, Hexagon) and isinstance(target, Star):
            return 1.5  # 六边形克制星形
        elif isinstance(self, Star) and isinstance(target, Circle):
            return 1.5  # 星形克制圆形
        else:
            return 1.0  # 默认倍率

    def take_damage(self, damage):
        self.health -= damage
        self.health = round(self.health, 0)  # 四舍五入到整数
        if self.health <= 0:
            self.is_alive = False
    def draw(self, screen):
        """绘制形状"""
        if not self.is_alive:
            return
        # 绘制名字和生命值
        name_text = chinese_font.render(f"{self.name} Lv{self.level} ♥{max(0, self.health)}", True, WHITE)
        screen.blit(name_text, (self.x - 50, self.y - 50))

    def move_towards(self):
        """向目标位置移动"""
        if self.target_x is None or self.target_y is None:
            return
        # 计算方向向量
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = (dx**2 + dy**2) ** 0.5
        if distance > self.speed:
            # 归一化方向向量并移动
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed
        else:
            # 如果已经接近目标，则直接到达目标
            self.x = self.target_x
            self.y = self.target_y
            self.target_x = None
            self.target_y = None
            self.is_moving = False

    def set_target(self, target_x, target_y):
        """设置目标位置"""
        self.target_x = target_x
        self.target_y = target_y
        self.is_moving = True

    def update_cooldown(self):
        """更新攻击冷却时间"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        for skill in self.skill_cooldowns:
            if self.skill_cooldowns[skill] > 0:
                self.skill_cooldowns[skill] -= 1

    def gain_exp(self, amount):
        """获取经验值"""
        self.exp += amount
        if self.exp >= self.exp_to_next_level:
            self.level_up()

    def level_up(self):
        """升级"""
        self.level += 1
        self.health += 20
        self.attack_damage += 3
        self.exp -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        print(f"{self.name} 升级了！当前等级：Lv{self.level}")

    def use_skill(self, skill_name, targets=None):
        """使用技能"""
        if self.skill_cooldowns[skill_name] > 0:
            return  # 如果技能冷却未完成，则无法使用
        if skill_name == "range_attack":
            self.range_attack(targets)
        elif skill_name == "heal":
            self.heal(targets)
        elif skill_name == "teleport":
            self.teleport()
        elif skill_name == "ultimate":
            self.ultimate(targets)
        # 设置技能冷却时间
        self.skill_cooldowns[skill_name] = 120  # 冷却时间为 120 帧（约 2 秒）

    def range_attack(self, targets):
        """范围攻击"""
        print(f"{self.name} 发动范围攻击！")
        for target in targets:
            if target.is_alive and target.team != self.team:
                damage = self.attack_damage * 0.8
                target.take_damage(damage)
                print(f"{self.name} ➔ 攻击 ➔ {target.name}，造成 {damage} 点伤害")

    def heal(self, targets):
        """治疗技能"""
        print(f"{self.name} 使用治疗技能！")
        for target in targets:
            if target.is_alive and target.team == self.team:
                heal_amount = 30
                target.health += heal_amount
                print(f"{self.name} 治愈了 {target.name}，回复 {heal_amount} 点生命")

    def teleport(self):
        """传送技能"""
        print(f"{self.name} 使用传送技能！")
        self.x = random.randint(100, SCREEN_WIDTH - 100)
        self.y = random.randint(100, SCREEN_HEIGHT - 100)

    def ultimate(self, targets):
        """终极技能"""
        print(f"{self.name} 发动终极技能！")
        for target in targets:
            if target.is_alive and target.team != self.team:
                damage = self.attack_damage * 2
                target.take_damage(damage)
                print(f"{self.name} ➔ 攻击 ➔ {target.name}，造成 {damage} 点伤害")


class Circle(Shape):
    def __init__(self, x, y, team=None):
        super().__init__("⚪ 圆形", health=150, attack_damage=10, color=BLUE, x=x, y=y, team=team)

    def draw(self, screen):
        super().draw(screen)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 30)

    def special_ability(self, base_damage, target):
        if random.random() < 0.2:
            bonus = int(base_damage * 0.5)
            print(f"{self.name} 发动碾压攻击！额外造成{bonus}点伤害")
            return base_damage + bonus
        return base_damage

    def evolve(self):
        """升阶为旋风骑士"""
        print(f"{self.name} 升阶为 🌀 旋风骑士！")
        new_shape = WhirlwindKnight(self.x, self.y, team=self.team)
        new_shape.health = self.health  # 继承当前生命值
        new_shape.exp = self.exp  # 继承当前经验值
        new_shape.level = self.level  # 继承当前等级
        arena.replace_shape(self, new_shape)  # 替换当前形状


class Triangle(Shape):
    def __init__(self, x, y, team=None):
        super().__init__("🔺 三角", health=120, attack_damage=15, color=RED, x=x, y=y, team=team)

    def draw(self, screen):
        super().draw(screen)
        pygame.draw.polygon(
            screen,
            self.color,
            [
                (int(self.x), int(self.y - 30)),
                (int(self.x - 30), int(self.y + 30)),
                (int(self.x + 30), int(self.y + 30)),
            ],
        )

    def special_ability(self, base_damage, target):
        if random.random() < 0.3:
            print(f"{self.name} 触发致命尖刺！暴击伤害！")
            return int(base_damage * 1.8)
        return base_damage

    def evolve(self):
        """升阶为烈焰战刃"""
        print(f"{self.name} 升阶为 🔥 烈焰战刃！")
        new_shape = FlameBlade(self.x, self.y, team=self.team)
        new_shape.health = self.health
        new_shape.exp = self.exp
        new_shape.level = self.level
        arena.replace_shape(self, new_shape)


class Square(Shape):
    def __init__(self, x, y, team=None):
        super().__init__("🟦 方形", health=200, attack_damage=8, color=GREEN, x=x, y=y, team=team)

    def draw(self, screen):
        super().draw(screen)
        pygame.draw.rect(screen, self.color, (int(self.x - 30), int(self.y - 30), 60, 60))

    def evolve(self):
        """升阶为钢铁堡垒"""
        print(f"{self.name} 升阶为 🛡️ 钢铁堡垒！")
        new_shape = SteelFortress(self.x, self.y, team=self.team)
        new_shape.health = self.health  # 继承当前生命值
        new_shape.exp = self.exp  # 继承当前经验值
        new_shape.level = self.level  # 继承当前等级
        arena.replace_shape(self, new_shape)  # 替换当前形状

    def special_ability(self, base_damage, target):
        self.health += 5
        print(f"{self.name} 的防御结构生效，回复5点生命")
        return base_damage


class Hexagon(Shape):
    def __init__(self, x, y, team=None):
        super().__init__("⬢ 六边形", health=180, attack_damage=12, color=YELLOW, x=x, y=y, team=team)

    def draw(self, screen):
        super().draw(screen)
        points = [
            (int(self.x), int(self.y - 30)),
            (int(self.x + 26), int(self.y - 15)),
            (int(self.x + 26), int(self.y + 15)),
            (int(self.x), int(self.y + 30)),
            (int(self.x - 26), int(self.y + 15)),
            (int(self.x - 26), int(self.y - 15)),
        ]
        pygame.draw.polygon(screen, self.color, points)

    def special_ability(self, base_damage, target):
        print(f"{self.name} 发动范围攻击！")
        return base_damage * 1.2

    def evolve(self):
        """升阶为水晶法师"""
        print(f"{self.name} 升阶为 🔮 水晶法师！")
        new_shape = CrystalMage(self.x, self.y, team=self.team)
        new_shape.health = self.health
        new_shape.exp = self.exp
        new_shape.level = self.level
        arena.replace_shape(self, new_shape)


class Star(Shape):
    def __init__(self, x, y, team=None):
        super().__init__("⭐ 星形", health=100, attack_damage=20, color=WHITE, x=x, y=y, team=team)

    def draw(self, screen):
        super().draw(screen)
        points = [
            (int(self.x), int(self.y - 30)),
            (int(self.x + 10), int(self.y - 10)),
            (int(self.x + 30), int(self.y - 10)),
            (int(self.x + 15), int(self.y + 10)),
            (int(self.x + 20), int(self.y + 30)),
            (int(self.x), int(self.y + 20)),
            (int(self.x - 20), int(self.y + 30)),
            (int(self.x - 15), int(self.y + 10)),
            (int(self.x - 30), int(self.y - 10)),
            (int(self.x - 10), int(self.y - 10)),
        ]
        pygame.draw.polygon(screen, self.color, points)

    def special_ability(self, base_damage, target):
        print(f"{self.name} 发动穿透攻击！")
        return base_damage * 1.5

    def evolve(self):
        """升阶为暗影刺客"""
        print(f"{self.name} 升阶为 🌟 暗影刺客！")
        new_shape = AssassinStar(self.x, self.y, team=self.team)
        new_shape.health = self.health
        new_shape.exp = self.exp
        new_shape.level = self.level
        arena.replace_shape(self, new_shape)

#---------------------------------------------------

class WhirlwindKnight(Circle):
    def __init__(self, x, y, team=None):
        super().__init__(x, y, team=team)
        self.name = "🌀 旋风骑士"
        self.health = 200
        self.attack_damage = 15

    def special_ability(self, base_damage, target):
        if random.random() < 0.3:
            print(f"{self.name} 发动旋风斩！")
            return base_damage * 1.5
        return base_damage

    def heal(self, targets):
        print(f"{self.name} 使用治疗之环！")
        for target in targets:
            if target.is_alive and target.team == self.team:
                heal_amount = 40
                target.health += heal_amount
                print(f"{self.name} 治愈了 {target.name}，回复 {heal_amount} 点生命")


class FlameBlade(Triangle):
    def __init__(self, x, y, team=None):
        super().__init__(x, y, team=team)
        self.name = "🔥 烈焰战刃"
        self.health = 150
        self.attack_damage = 25

    def special_ability(self, base_damage, target):
        if random.random() < 0.4:
            print(f"{self.name} 触发致命烈焰！暴击伤害！")
            return int(base_damage * 2.0)
        return base_damage

    def flame_storm(self, targets):
        print(f"{self.name} 发动火焰风暴！")
        for target in targets:
            if target.is_alive and target.team != self.team:
                damage = self.attack_damage * 1.5
                target.take_damage(damage)
                print(f"{self.name} ➔ 攻击 ➔ {target.name}，造成 {damage} 点伤害")
    def flame_shield(self):
        """火焰护盾：减少受到的伤害"""
        print(f"{self.name} 启动火焰护盾！")
        self.health += 30
        print(f"{self.name} 获得护盾效果，回复 30 点生命")


class SteelFortress(Square):
    def __init__(self, x, y, team=None):
        super().__init__(x, y, team=team)
        self.name = "🛡️ 钢铁堡垒"
        self.health = 300
        self.attack_damage = 15

    def special_ability(self, base_damage, target):
        self.health += 10
        print(f"{self.name} 的钢铁结构生效，回复 10 点生命")
        return base_damage

    def steel_barrier(self):
        print(f"{self.name} 启动钢铁壁垒！")
        self.health += 50
        print(f"{self.name} 强化防御，回复 50 点生命")

class CrystalMage(Hexagon):
    def __init__(self, x, y, team=None):
        super().__init__(x, y, team=team)
        self.name = "🔮 水晶法师"
        self.health = 200
        self.attack_damage = 25

    def special_ability(self, base_damage, target):
        if random.random() < 0.5:
            print(f"{self.name} 发动水晶冲击！")
            return base_damage * 1.8
        return base_damage

    def teleport(self):
        print(f"{self.name} 使用水晶传送！")
        self.x = random.randint(100, SCREEN_WIDTH - 100)
        self.y = random.randint(100, SCREEN_HEIGHT - 100)

class AssassinStar(Star):
    def __init__(self, x, y, team=None):
        super().__init__(x, y, team=team)
        self.name = "🌟 暗影刺客"
        self.health = 120
        self.attack_damage = 30

    def special_ability(self, base_damage, target):
        if random.random() < 0.5:
            print(f"{self.name} 触发致命一击！")
            return base_damage * 2
        return base_damage

    def poison_blade(self, target):
        print(f"{self.name} 使用毒刃攻击！")
        poison_damage = 10
        target.take_damage(poison_damage)
        print(f"{self.name} 对 {target.name} 附加中毒效果，额外造成 {poison_damage} 点伤害")


class Arena:
    def __init__(self):
        self.shapes = []
        self.frame_counter = 0  # 新增：帧计数器

    def replace_shape(self, old_shape, new_shape):
        """替换竞技场中的形状"""
        index = self.shapes.index(old_shape)
        self.shapes[index] = new_shape
        print(f"{old_shape.name} 已被替换为 {new_shape.name}")

    def add_shape(self, shape):
        self.shapes.append(shape)

    def show_status(self):
        for shape in self.shapes:
            if shape.is_alive:
                shape.draw(screen)

    def run_battle(self):
        round = 1
        running = True
        clock = pygame.time.Clock()
        while running:
            screen.fill(BLACK)  # 清屏
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # 更新冷却时间
            for shape in self.shapes:
                if shape.is_alive:
                    shape.update_cooldown()

            # 每 60 帧执行一次战斗逻辑
            self.frame_counter += 1
            if self.frame_counter % 60 == 0:  # 控制回合速度
                # 检查是否只剩下一个存活的形状
                survivors = [s for s in self.shapes if s.is_alive]
                if len(survivors) <= 1:
                    break

                # 攻击逻辑
                for shape in self.shapes:
                    if shape.is_alive and not shape.is_moving:
                        # 获取所有存活的形状
                        targets = [s for s in self.shapes if s.is_alive and s != shape]

                        # 如果没有其他团队的目标，则开始自相残杀
                        if all(s.team == shape.team for s in targets):
                            print(f"⚠️ {shape.name} 开始自相残杀！")
                            targets = [s for s in targets if s != shape]  # 攻击同团队的目标
                        else:
                            # 否则优先攻击不同团队的目标
                            targets = [s for s in targets if s.team != shape.team]

                        if not targets:  # 如果没有有效目标，跳过
                            print(f"{shape.name} 没有可攻击的目标，跳过回合！")
                            continue

                        target = random.choice(targets)
                        # 设置目标位置
                        shape.set_target(target.x, target.y)

                        # 尝试使用技能
                        if isinstance(shape, WhirlwindKnight):
                            if shape.skill_cooldowns["range_attack"] == 0:
                                shape.use_skill("range_attack", targets)
                            elif shape.skill_cooldowns["heal"] == 0:
                                shape.use_skill("heal", [s for s in self.shapes if s.team == shape.team])
                        elif isinstance(shape, CrystalMage):
                            if shape.skill_cooldowns["teleport"] == 0:
                                shape.use_skill("teleport")
                            elif shape.skill_cooldowns["ultimate"] == 0:
                                shape.use_skill("ultimate", targets)
                        elif isinstance(shape, AssassinStar):
                            if random.random() < 0.3:
                                shape.poison_blade(target)

            # 更新形状的位置
            for shape in self.shapes:
                if shape.is_alive:
                    if shape.is_moving:
                        shape.move_towards()
                    else:
                        # 当到达目标时发起攻击
                        if shape.target_x is None and shape.target_y is None:
                            for target in self.shapes:
                                if target.is_alive and target.x == shape.x and target.y == shape.y:
                                    damage = shape.attack(target)
                                    if damage > 0:
                                        print(f"{shape.name} ➔ 攻击 ➔ {target.name}，造成 {damage} 点伤害")

                                    # 检查目标状态
                                    if not target.is_alive:
                                        print(f"✨ {target.name} 被击败了！")
                                        shape.gain_exp(50)  # 击败敌人获得经验
                                        shape.level_up()  # 调用正确的升级方法
                                    break

            # 显示当前战况
            self.show_status()

            # 更新屏幕
            pygame.display.flip()
            clock.tick(60)  # 提高帧率到 60 FPS

        # 宣布胜利者
        survivors = [s for s in self.shapes if s.is_alive]
        if survivors:
            winner_text_parts = render_text_with_emoji(f"🎉 最终胜利者：{survivors[0].name}", WHITE)
            y_position = SCREEN_HEIGHT // 2
            x_offset = 0
            for text, offset in winner_text_parts:
                screen.blit(text, (SCREEN_WIDTH // 2 - 150 + x_offset, y_position))
                x_offset += offset
            print(f"🎉 最终胜利者：{survivors[0].name}")
        else:
            draw_text_parts = render_text_with_emoji("💥 全部同归于尽了！", WHITE)
            y_position = SCREEN_HEIGHT // 2
            x_offset = 0
            for text, offset in draw_text_parts:
                screen.blit(text, (SCREEN_WIDTH // 2 - 150 + x_offset, y_position))
                x_offset += offset
            print("💥 全部同归于尽了！")

        # 更新屏幕以显示胜利者或平局信息
        pygame.display.flip()

        # 等待 3 秒钟以便玩家看到结果
        time.sleep(3)

        # 退出 Pygame
        pygame.quit()

        # 结束程序
        exit()


def render_text_with_emoji(text, color):
    """渲染包含中文和表情符号的文本"""
    parts = text.split("🎉")  # 根据表情符号分割文本
    rendered_texts = []
    total_width = 0
    for i, part in enumerate(parts):
        # 渲染中文部分
        if part:
            chinese_text = chinese_font.render(part, True, color)
            rendered_texts.append((chinese_text, chinese_text.get_width()))
            total_width += chinese_text.get_width()
        # 渲染表情符号部分
        if i < len(parts) - 1:  # 如果不是最后一部分，说明后面有表情符号
            emoji_text = emoji_font.render("🎉", True, color)
            rendered_texts.append((emoji_text, emoji_text.get_width()))
            total_width += emoji_text.get_width()
    return rendered_texts

# ---------- 新增功能实现部分 ----------

class GridSystem:
    def __init__(self):
        self.cell_size = 50
        self.offset = 0
        self.color = (40, 40, 60)

    def update(self):
        pass
        # self.offset = (self.offset + 1) % 100
        # r = 40 + int(15 * math.sin(self.offset / 10))
        # self.color = (r, 40, 60 + int(20 * math.cos(self.offset / 15)))

    def draw(self, surface):
        for x in range(0, SCREEN_WIDTH, self.cell_size):
            pygame.draw.line(surface, self.color,
                             (x + self.offset % self.cell_size, 0),
                             (x + self.offset % self.cell_size, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, self.cell_size):
            pygame.draw.line(surface, self.color,
                             (0, y + (self.offset * 2) % self.cell_size),
                             (SCREEN_WIDTH, y + (self.offset * 2) % self.cell_size))


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.life = 30
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            size = int(self.life / 5) + 1
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add_explosion(self, x, y):
        for _ in range(20):
            self.particles.append(Particle(x, y, (255, random.randint(100, 200), 0)))

    def update(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)


class WeatherSystem:
    def __init__(self):
        self.rain_drops = []
        self.intensity = 50

    def update(self):
        # 添加新雨滴
        if random.random() < 0.3:
            self.rain_drops.append((
                random.randint(0, SCREEN_WIDTH),
                random.randint(-50, 0),
                random.randint(3, 6)
            ))
        # 更新位置
        self.rain_drops = [(x, y + s, s) for x, y, s in self.rain_drops if y < SCREEN_HEIGHT]

    def draw(self, surface):
        for x, y, s in self.rain_drops:
            pygame.draw.line(surface, (150, 150, 255), (x, y), (x, y + 10), 2)


class TerrainSystem:
    def __init__(self):
        self.obstacles = [
            pygame.Rect(200, 200, 100, 100),
            pygame.Rect(500, 400, 80, 80)
        ]
        self.height_map = [[random.randint(0, 10) for _ in range(16)] for _ in range(12)]

    def get_height(self, x, y):
        gx = min(max(int(x / 50), 0), 15)
        gy = min(max(int(y / 50), 0), 11)
        return self.height_map[gy][gx]

    def draw(self, surface):
        # 绘制地形高度
        for y in range(12):
            for x in range(16):
                h = self.height_map[y][x]
                color = (0, 50 + h * 15, 0)
                pygame.draw.rect(surface, color, (x * 50, y * 50, 50, 50))
        # 绘制障碍物
        for rect in self.obstacles:
            pygame.draw.rect(surface, (100, 80, 60), rect)


class CameraSystem:
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 1.0
        self.target = None

    def update(self):
        if self.target:
            self.offset_x = SCREEN_WIDTH / 2 - self.target.x * self.zoom
            self.offset_y = SCREEN_HEIGHT / 2 - self.target.y * self.zoom

    def apply(self, pos):
        return (pos[0] * self.zoom + self.offset_x,
                pos[1] * self.zoom + self.offset_y)


class EnhancedArena(Arena):
    def __init__(self):
        super().__init__()
        self.grid = GridSystem()
        self.particles = ParticleSystem()
        self.weather = WeatherSystem()
        self.terrain = TerrainSystem()
        self.camera = CameraSystem()
        self.selected = None

    def show_status(self):
        # 更新系统
        self.grid.update()
        self.particles.update()
        self.weather.update()
        self.camera.update()

        # 绘制背景元素
        screen.fill(BLACK)
        self.terrain.draw(screen)
        self.grid.draw(screen)
        self.weather.draw(screen)

        # 绘制原始内容
        for shape in self.shapes:
            if shape.is_alive:
                # 应用摄像机变换
                draw_pos = self.camera.apply((shape.x, shape.y))
                # 绘制血条
                self.draw_health_bar(shape, draw_pos)
                # 绘制冷却环
                self.draw_cooldown(shape, draw_pos)
                # 绘制本体
                self.draw_shape(shape, draw_pos)
                # 绘制选中效果
                if shape == self.selected:
                    pygame.draw.circle(screen, YELLOW, (int(draw_pos[0]), int(draw_pos[1])), 35, 3)

        # 绘制粒子效果
        self.particles.draw(screen)

    def draw_shape(self, shape, pos):
        # 根据类型调用原始绘制方法（需调整坐标）
        original_x, original_y = shape.x, shape.y
        shape.x, shape.y = pos
        shape.draw(screen)
        shape.x, shape.y = original_x, original_y  # 恢复原始坐标

    def draw_health_bar(self, shape, pos):
        bar_width = 60
        bar_height = 6
        fill = (shape.health / 150) * bar_width
        pygame.draw.rect(screen, RED, (pos[0] - 30, pos[1] - 60, fill, bar_height))
        pygame.draw.rect(screen, (80, 80, 80), (pos[0] - 30, pos[1] - 60, bar_width, bar_height), 2)

    def draw_cooldown(self, shape, pos):
        if shape.attack_cooldown > 0:
            radius = 15
            angle = (shape.attack_cooldown / 60) * 360
            rect = (pos[0] - 15, pos[1] + 20, 30, 30)
            pygame.draw.arc(screen, BLUE, rect, math.radians(-90), math.radians(angle - 90), 3)

    def run_battle(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # 鼠标选择事件
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    for shape in self.shapes:
                        dx = (shape.x * self.camera.zoom + self.camera.offset_x) - mx
                        dy = (shape.y * self.camera.zoom + self.camera.offset_y) - my
                        if dx ** 2 + dy ** 2 < 900:  # 30像素选择半径
                            self.selected = shape
                            self.camera.target = shape

            # 地形效果应用
            for shape in self.shapes:
                height = self.terrain.get_height(shape.x, shape.y)
                shape.attack_damage += height // 5

                # 障碍物碰撞检测
                for obstacle in self.terrain.obstacles:
                    if obstacle.collidepoint(shape.x, shape.y):
                        shape.health += 1  # 获得防御加成

            # 组队连携检测
            for shape in self.shapes:
                teammates = [s for s in self.shapes if s.team == shape.team and s != shape]
                if len(teammates) >= 2:
                    for t in teammates:
                        if math.hypot(shape.x - t.x, shape.y - t.y) < 100:
                            shape.attack_damage += 5
                            self.particles.add_explosion(shape.x, shape.y)

            # 调用原始战斗逻辑
            super().run_battle()

            # 控制帧率
            clock.tick(60)


# ---------- 初始化增强竞技场 ----------
arena = EnhancedArena()

# 新团队列表
teams = ["Team A", "Team B", "Team C"]

# 初始形状类列表
initial_shapes_classes = [Circle, Triangle, Square, Hexagon, Star]
# 进阶形状类列表
advanced_shapes_classes = [WhirlwindKnight, CrystalMage, AssassinStar, FlameBlade, SteelFortress]

# 生成初始单位
for _ in range(8):  # 添加 8 个单位
    ShapeClass = random.choice(initial_shapes_classes+advanced_shapes_classes)  # 随机选择形状类型
    team = random.choice(teams)  # 随机分配团队
    x = random.randint(100, SCREEN_WIDTH - 100)  # 随机生成 x 坐标
    y = random.randint(100, SCREEN_HEIGHT - 100)  # 随机生成 y 坐标
    arena.add_shape(ShapeClass(x, y, team=team))  # 将形状添加到竞技场

arena.run_battle()
pygame.quit()