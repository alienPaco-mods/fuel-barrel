# Fuel Barrel — Build 42 prototype (v0.4.1)

**Status: experimental.** Back up your save before enabling.

## Install

Copy this folder to `~/Zomboid/mods/FuelBarrel`. The game does not follow a symlinked mod folder reliably, so use a real copy.

## How it works

1. **Craft a Fuel Barrel** (Metalworking, Welding 6): welding mask (kept), 4 blowtorch uses, 4 sheet metal, 4 welding rods. It is an inventory item that holds 120 L of any liquid by default.
   Or craft a **Crude Fuel Barrel** at Welding 4: welding mask (kept), 2 blowtorch uses, 2 sheet metal, 2 welding rods. It holds 60 L by default and works the same way.
2. Right-click a generator with a rubber hose and pliers in your inventory and choose **Connect Fuel Barrel**, either directly or in the **Generator** submenu (for a Crude barrel the options and the submenu read **Crude Fuel Barrel**). The barrel can be in your inventory or on the ground on the generator's square or one of the eight around it (same floor). A carried barrel is used first. The barrel and hose are used up, and the pliers are kept. The barrel must be empty or hold only gasoline.
3. The generator's sprite changes to show the barrel, and the barrel keeps the generator's 10 L tank topped up. The barrel level appears in the generator's info window.
4. Fill the connected barrel from the **Fuel Barrel** submenu when you right-click the generator.
5. **Disconnect Fuel Barrel**, in the same submenu, gives you the barrel and hose back, at the size it was crafted with. It also needs pliers, which are kept. The barrel must be completely empty first, and the generator can't be picked up while a barrel is connected.

## Sandbox options

**Fuel Barrel capacity** and **Crude Fuel Barrel capacity** are under Fuel Barrel in the sandbox options. They apply to barrels crafted from then on.

`luajit tests/test_barrel.lua` checks the barrel types and capacities. `luajit tests/test_unload.lua` runs the feed through unload and reload cycles against a model of the generator's own billing.

## Rebuilding the art

`tools/build_tileset.py` paints each barrel style, after vanilla's metal drums, and composites it with the 16 vanilla generator sprites (needs Pillow). Colours and sizes are at the top. It rewrites `42/media/fuelbarrel.tiles`, `42/media/texturepacks/fuelbarrel.pack` and the item icon.

`tools/build_model.py` generates the 3D models shown when a barrel is on the ground (needs Pillow and numpy). It rewrites the `.glb` files in `42/media/Models_X` and each `Model.png` texture. Their in-game size is the `scale` line in each `model` block in `42/media/scripts/FuelBarrel.txt`.

## Known prototype caveats

- The vanilla generator tank stays at 10 L, because the engine hardcodes it. The barrel adds its own capacity on top by refilling that tank once per in-game minute.
- A connected barrel only accepts gasoline. A barrel contaminated before this rule existed will not feed until it is emptied.
- If the generator runs out while you are away, the barrel pays for the missed hours and restarts it a moment after you return.
- Destroying a generator loses the connected barrel and its contents.
- Fuel weighs 1 per litre, on top of the barrel (15, Crude 8). A loaded barrel may be too heavy to pick up, which is why it can be connected from the ground. Vanilla's pump only fills carried containers, up to your free carrying room. A trunk counts the fuel against its capacity.
- `tiledef` number 5128 must be unique among your active mods.
- Multiplayer is not supported. This mod is singleplayer only for now.

## Engineering notes

The barrel's real `FluidContainer` component moves onto the generator with `GameEntityFactory.TransferComponent`, so it saves with the generator and vanilla's fluid UI works on it. The combined sprite is an overlay that fully covers the generator, so the generator keeps its vanilla sprite and `getGeneratorItemType()` still returns the right model.
