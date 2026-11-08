# FUEL BARREL
### The Official Player's Guide

> *"A generator is only as good as the fuel you can keep beside it."*

---

## Contents
1. What This Mod Does
2. Quick Start
3. The Two Barrels
4. Connecting a Barrel
5. Filling Up
6. Disconnecting
7. While You're Away
8. The Fuelman's Ledger
9. Tips
10. Troubleshooting
11. Sandbox Settings
12. Appendix: The Tester's Toolkit

---

## 1. What This Mod Does

A vanilla generator holds **10 L** of gasoline, and somebody has to come back and refill it. This mod lets you weld a **Fuel Barrel**, hose it to the generator, and let the barrel keep the tank topped up for you.

**A standard barrel holds 120 L: twelve vanilla tankfuls.** It keeps working while you are away, so a generator at a base you've left behind keeps the freezer cold.

**Build 42 only (42.20 or newer). Singleplayer only.**

---

## 2. Quick Start

1. **Weld a barrel** from the crafting menu, at a table or counter: Welding 6 for the Fuel Barrel, Welding 4 for the Crude one.
2. Carry a **Rubber Hose** and **pliers**, and either carry the barrel or set it down next to the generator. Right-click the generator and pick **Connect Fuel Barrel**.
3. Right-click the generator again, open **Fuel Barrel** and **pour gasoline in**.
4. That's it. The generator now runs on the barrel.

---

## 3. The Two Barrels

| | **Fuel Barrel** | **Crude Fuel Barrel** |
|---|---|---|
| Holds | **120 L** | **60 L** |
| Vanilla tankfuls | 12 | 6 |
| With the generator's own tank | 130 L | 70 L |
| Weight (empty) | 15.0 | 8.0 |
| Welding needed | 6 | 4 |
| Welding mask | 1 (kept) | 1 (kept) |
| Blowtorch uses | 4 | 2 |
| Sheet Metal | 4 | 2 |
| Welding Rods | 4 | 2 |
| Welding XP | 60 | 30 |

Both work the same way. The Crude barrel is the one you can make early, from scrap, with half the metal.

> **Margin note: why not just a bigger tank?** The game fixes every generator's tank at 10 L. The barrel doesn't change that. It sits beside the generator and pours into the tank every in-game minute, so the tank never gets low while there's fuel in the barrel.

Both sizes can be changed in the sandbox settings (see 11). A barrel keeps the size it was crafted with, even after you change the setting, and even after you disconnect it and carry it to another generator.

---

## 4. Connecting a Barrel

**You need:** a **Rubber Hose** (used up) and **pliers** (kept) in your inventory, and the barrel either **in your inventory** or **lying on the ground next to the generator**: on its square or any of the eight around it, on the same floor.

Right-click the generator and pick **Connect Fuel Barrel** (it's also in the **Generator** submenu). Your character kneels and hoses it up. If you carry a barrel and another lies nearby, the one you carry is used.

- The barrel must be **empty or hold only gasoline**.
- The generator can be on or off.
- The generator's sprite changes to show the barrel standing beside it.
- **Generator Info** now shows the barrel level on its first line: *"Fuel Barrel: 87 / 120 L"*.

If the option is red, hover over it for the reason: no hose, no pliers, or something other than gasoline in the barrel.

---

> **Margin note: why the ground?** A barrel with fuel in it is heavy, and you can't pick up more than you have room to carry. Real drums are never carried full, they're rolled. So a barrel can be connected where it stands.

## 5. Filling Up

Right-click the generator and open the **Fuel Barrel** submenu. That's the barrel's own liquid menu, so you can pour into it from any gas can or container, the same way you'd fill a rain barrel.

- **A connected barrel only takes gasoline.** Nothing else goes in.
- The barrel feeds the tank, never the other way round.
- You can top it up while the generator runs.

### The weight of fuel

Every litre of fuel weighs **1**, on top of the barrel itself.

| Fuel in it | Fuel Barrel | Crude Fuel Barrel |
|---|---|---|
| Empty | 15 | 8 |
| 30 L | 45 | 38 |
| 60 L | 75 | **68 (full)** |
| 100 L | 115 | |
| 120 L | **135 (full)** | |

The weight decides what you can do with it:

| You want to... | The rule |
|---|---|
| **Pick it up** | Only if it fits in your free carrying room, like any item. A full barrel won't. |
| **Fill it at a gas pump** | **Take Gas from Pump** only fills containers you carry, and only as much as you still have room to carry. So one fill gives roughly what your inventory has left. |
| **Drop it** | Always. A floor square normally holds 50, but the game lets a single heavier item onto an empty square. |
| **Load it into a car** | The trunk counts the fuel too. Most trunks hold 130 in good repair and some hold 160. A damaged trunk holds less, and anything already in it counts. A full Crude barrel fits most cars. A full Fuel Barrel needs a big, empty, undamaged one. A 130 trunk takes it with up to 115 L in. |
| **Connect it** | Carried or lying beside the generator. Weight doesn't matter. |

### Bringing fuel home in bulk

1. Drive to the gas station with an empty barrel and some gas cans.
2. Drop the barrel by the pump. Fill the cans at the pump and pour them into the barrel on the ground from its liquid menu (right-click it). Fill the barrel in your inventory first if you like, up to your carrying room, then drop it.
3. Move the barrel from the floor into the trunk, using the trunk's loot window. You don't have to lift it to do this.
4. Drive to the generator, take the barrel out of the trunk onto the ground beside the generator, and **Connect Fuel Barrel**.

> **Field note:** an empty barrel in the trunk and a few gas cans make one trip worth 60 or 120 L. With only gas cans, the same fuel is a lot of trips back and forth to the generator.

---

## 6. Disconnecting

Open the **Fuel Barrel** submenu and pick **Disconnect Fuel Barrel**. It needs pliers (kept). You get the barrel and the hose back.

- **The barrel must be completely empty first.** Drain it into gas cans.
- **You can't pick up the generator while a barrel is connected.** Disconnect it first.

---

## 7. While You're Away

When you leave, the game stops running that part of the map. When you come back, the generator pays for the hours you were gone **from its own 10 L tank only**, and switches off if that runs dry.

The barrel then settles the rest of the bill:

| Time away | What you find |
|---|---|
| Short, the tank covered it | Still running. The barrel tops the tank up again. |
| Long, the barrel covers the rest | Still running. The barrel pays for the missing hours, and the generator restarts a moment after you arrive. |
| Longer than the fuel lasts | Off, with the barrel empty. It ran out while you were gone. |

> **Margin note: the bill.** Say the generator burns 0.5 L an hour and you were gone 60 hours. That's 30 L. The tank pays its 10 L, runs dry and switches off. The barrel pays the other 20 L and starts it again. It's the same fuel, and the same wear, as if it had run the whole time.

**Wear still counts.** A running generator loses condition now and then, and the barrel pays for that too. Every hour it rolls a die. On a hit it loses 1 or 2 condition. A generator at 0 condition is not restarted.

| Generator | Chance per hour | Condition lost per 100 hours (average) |
|---|---|---|
| Premium Technologies (yellow) | 1 in 36 | about 4 |
| Lectromax | 1 in 30 | about 5 |
| Old | 1 in 25 | about 6 |
| ValuTech (blue) | 1 in 24 | about 6 |

> **Why it works:** a yellow Premium Technologies generator on a full barrel will see out a long winter with condition to spare. A ValuTech wears half again as fast. Spend your Electrical skill on the one you leave behind.

---

## 8. The Fuelman's Ledger

**How long will it last?** Open **Generator Info**. Under **Power Consumption** it shows how many litres an hour the generator burns with what's plugged in. Divide the barrel by that number:

| Burn rate (L/h) | 10 L tank alone | Crude barrel + tank (70 L) | Fuel Barrel + tank (130 L) |
|---|---|---|---|
| 0.1 | 4 days | 29 days | 54 days |
| 0.25 | 1.7 days | 12 days | 22 days |
| 0.5 | 20 hours | 6 days | 11 days |
| 1.0 | 10 hours | 3 days | 5.4 days |

Every fridge, freezer, light and stove you add raises the rate, and so does the sandbox's **Generator Fuel Consumption** setting. Unplug what you don't need before a long trip.

> **Real-world notebook: the day tank.** Real standby generators work just like this. The engine has a small "day tank" beside it, and a large bulk tank keeps refilling it through a pipe. The small tank stays close to the engine and quick to feed. The big one holds the reserve.

> **Real-world notebook: the drum.** The steel drum you see at every farm and garage is a 55-gallon drum, about 208 L. The mod's 120 L barrel is closer to the smaller 30-gallon drum (about 114 L), the size one person can still drag around empty.

> **Real-world notebook: the hose.** Ordinary natural rubber swells and goes soft in gasoline. Real fuel hose is made from synthetic rubbers such as nitrile, which shrug it off. The game doesn't tell its hoses apart, so any Rubber Hose will do.

> **Real-world notebook: stale fuel.** Real gasoline goes stale in storage. Within months it loses its lighter parts and gums up engines unless a stabiliser is added. Project Zomboid doesn't model this, so a barrel filled in July still runs the generator at Christmas.

---

## 9. Tips

- **Crude first, standard later.** At Welding 4 a Crude barrel already gives you seven times the fuel of the tank alone.
- **Disconnect needs an empty barrel**, so plan a move: run it down, or drain it into cans.
- **Don't carry a barrel you mean to fill.** Leave it on the ground. A loaded barrel can't be picked up again, but it can be connected where it lies.
- **Keep a spare hose.** Every connection uses one up. Disconnecting gives it back.
- **Check Generator Info before leaving.** The first line shows the barrel level, the rest shows the burn rate, and the table above gives you the days.
- **A generator indoors still poisons the house**, barrel or no barrel. Keep it outside.

---

## 10. Troubleshooting

| Problem | Why | Fix |
|---|---|---|
| **Connect Fuel Barrel** is red | No hose, no pliers, or the barrel holds something other than gasoline | Hover over it for the reason |
| No **Connect** option at all | The barrel is neither carried nor on the ground right next to the generator | Move it to a square touching the generator, on the same floor |
| Can't pick the barrel up | Its fuel counts towards your carrying weight | Leave it on the ground and connect it there, or move it with a trunk |
| The pump fills only part of the barrel | The pump only fills as much as you can carry | Drop the barrel and pour gas cans into it |
| **Disconnect** is red | Fuel left in the barrel, or no pliers | Drain it completely |
| Can't pick up the generator | A barrel is connected | Disconnect it first |
| The barrel doesn't feed | It holds something besides gasoline (only possible in a barrel connected before the gasoline-only rule was added) | Empty it and refill with gasoline |
| Generator off when I came back | It ran out while you were away, or it broke down (0 condition) | Check the barrel level and the condition in Generator Info |
| The generator blew up | Vanilla: generators in bad condition can catch fire or explode | The barrel and its fuel are lost with it |

---

## 11. Sandbox Settings

Under **Fuel Barrel** in the sandbox options:

| Setting | Default | Range |
|---|---|---|
| Fuel Barrel capacity (L) | 120 | 20 to 500 |
| Crude Fuel Barrel capacity (L) | 60 | 20 to 500 |

They apply to barrels crafted from then on. A barrel already made keeps its size for good.

---

## 12. Appendix: The Tester's Toolkit

Fuel Barrel has no console commands of its own. To test it in a debug game (launch option `-debug`):

1. Spawn **Fuel Barrel** or **Crude Fuel Barrel**, **Rubber Hose**, **Pliers**, a **Gas Can** and a **Generator** from the debug item list.
2. Place the generator, connect the barrel, pour in the gas and switch the generator on. To test connecting from the ground, drop a part-filled barrel next to the generator first.
3. Note the barrel level in **Generator Info**, walk or drive well out of the area, sleep or wait a few in-game days, and come back. The barrel should be lower by the hours you were gone, and the generator still running.

Outside the game, from the mod folder:

| Command | What it checks |
|---|---|
| `luajit tests/test_barrel.lua` | Barrel types, sizes and the sandbox settings |
| `luajit tests/test_unload.lua` | The feed across leaving and coming back, including coming back only briefly, against a model of the generator's own fuel bill |
