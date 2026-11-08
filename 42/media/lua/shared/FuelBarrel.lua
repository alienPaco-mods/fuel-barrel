-- Fuel Barrel B42: connects a barrel to a generator. The generator's tank is
-- fixed at 10 L, so the barrel's own FluidContainer moves onto the generator and
-- keeps the tank topped up. Vanilla saves it and its fluid UI works on it.
FuelBarrel = FuelBarrel or {}

FuelBarrel.HOSE = "Base.RubberHose"

-- overlayBase follows overlay_base in tools/build_tileset.py.
FuelBarrel.TYPES = {
    { item = "FuelBarrel.FuelBarrel", textKey = "FuelBarrel", overlayBase = 1, capacity = 120, option = "Capacity" },
    { item = "FuelBarrel.CrudeFuelBarrel", textKey = "CrudeFuelBarrel", overlayBase = 17, capacity = 60, option = "CrudeCapacity" },
}

local TILESET_PREFIX = "fuelbarrel_01_"
local GENERATOR_PREFIX = "appliances_misc_01_"
local GENERATOR_SPRITE_COUNT = 16

local DEFAULT_WEAR_CHANCE = 30  -- matches IsoGenerator when its item has no value

-- The engine charges a loaded generator before Lua's next tick, so two ticks is always enough.
local RECOVERY_TICKS = 2

local tracked = {}
-- Generators back from time away, waiting for their first bill before the barrel pays the rest.
local pending = {}

function FuelBarrel.generatorSprites()
    local sprites = {}
    for i = 0, GENERATOR_SPRITE_COUNT - 1 do
        table.insert(sprites, GENERATOR_PREFIX .. i)
    end
    return sprites
end

-- The script's capacity is fixed when the game loads, so a barrel takes the sandbox's when crafted.
-- Barrels made earlier keep theirs.
function FuelBarrel.onCreateBarrel(craftRecipeData)
    local options = SandboxVars and SandboxVars.FuelBarrel
    local created = craftRecipeData:getAllCreatedItems()
    for i = 0, created:size() - 1 do
        local barrel = created:get(i)
        for _, barrelType in ipairs(FuelBarrel.TYPES) do
            if barrelType.item == barrel:getFullType() then
                barrel:getFluidContainer():setCapacity(options and options[barrelType.option] or barrelType.capacity)
            end
        end
    end
end

local function notBroken(item)
    return not item:isBroken()
end

function FuelBarrel.findPliers(inventory)
    return inventory:getFirstTagEvalRecurse(ItemTag.PLIERS, notBroken)
end

function FuelBarrel.getContainer(generator)
    return generator:getComponent(ComponentType.FluidContainer)
end

-- A generator whose barrel container went missing counts as bare, so it can be connected again.
function FuelBarrel.isAttached(generator)
    return generator:getModData().fuelBarrel ~= nil and FuelBarrel.getContainer(generator) ~= nil
end

-- Generators connected before there were two barrels hold the standard one.
function FuelBarrel.typeOf(generator)
    local item = generator:getModData().fuelBarrelItem
    for _, barrelType in ipairs(FuelBarrel.TYPES) do
        if barrelType.item == item then return barrelType end
    end
    return FuelBarrel.TYPES[1]
end

-- A barrel is an item in an inventory or one lying on the ground. Dropping an item moves its
-- FluidContainer onto the ground object, so the fuel is on whichever of the two holds it now.
function FuelBarrel.isOnGround(barrel)
    return instanceof(barrel, "IsoWorldInventoryObject")
end

local function fuelHolder(barrel)
    if FuelBarrel.isOnGround(barrel) and not barrel:getComponent(ComponentType.FluidContainer) then
        return barrel:getItem()
    end
    return barrel
end

function FuelBarrel.barrelContainer(barrel)
    return fuelHolder(barrel):getComponent(ComponentType.FluidContainer)
end

function FuelBarrel.barrelType(barrel)
    return FuelBarrel.isOnGround(barrel) and barrel:getItem():getFullType() or barrel:getFullType()
end

-- A barrel too full to carry can be connected where it lies, on the generator's square or next to it.
function FuelBarrel.findGroundBarrel(generator, itemType)
    local square = generator:getSquare()
    if not square then return end
    for dy = -1, 1 do
        for dx = -1, 1 do
            local nearby = getCell():getGridSquare(square:getX() + dx, square:getY() + dy, square:getZ())
            local items = nearby and nearby:getWorldObjects()
            for i = 0, items and items:size() - 1 or -1 do
                local worldItem = items:get(i)
                if worldItem:getItem() and worldItem:getItem():getFullType() == itemType then return worldItem end
            end
        end
    end
end

function FuelBarrel.holdsOnlyFuel(container)
    return container:isEmpty() or container:isPureFluid(Fluid.Petrol)
end

-- Tile numbers follow paint_generator in tools/build_tileset.py.
local function overlayName(generator)
    local index = tonumber(string.sub(generator:getSprite():getName(), #GENERATOR_PREFIX + 1))
    return index and TILESET_PREFIX .. (index + FuelBarrel.typeOf(generator).overlayBase) or nil
end

function FuelBarrel.refreshSprite(generator)
    generator:setOverlaySprite(FuelBarrel.isAttached(generator) and overlayName(generator) or nil)
end

-- Only applies while connected: detaching discards this container for a fresh barrel.
local function restrictToFuel(container)
    local filter = FluidFilter.new()
    filter:setFilterType(FluidFilter.FilterType.Whitelist)
    filter:add(Fluid.Petrol)
    container:setWhitelist(filter)
end

local function worldHours()
    return getGameTime():getWorldAgeHours()
end

-- A generator isn't simulated while unloaded. Its first update bills every missed hour
-- to the tank alone and shuts it off if the tank runs dry, so note what that bill will be.
local function noteTimeAway(generator, entry)
    local lastFed = generator:getModData().fuelBarrelLastFed
    if not lastFed or not generator:isActivated() then return end

    -- getTotalPowerUsing already includes the sandbox fuel consumption setting.
    entry.burnPerHour = generator:getTotalPowerUsing()
    entry.awayBurn = (worldHours() - lastFed) * entry.burnPerHour
    entry.tankWhenLoaded = generator:getFuel()
end

function FuelBarrel.track(generator)
    if not FuelBarrel.isAttached(generator) then
        -- Drop the barrel overlay of one whose container is gone.
        if generator:getModData().fuelBarrel then FuelBarrel.refreshSprite(generator) end
        return
    end

    local entry = {}
    tracked[generator] = entry
    restrictToFuel(FuelBarrel.getContainer(generator))
    noteTimeAway(generator, entry)
    if entry.awayBurn then
        entry.ticks = RECOVERY_TICKS
        pending[generator] = entry
    end
    FuelBarrel.refreshSprite(generator)
end

function FuelBarrel.attach(generator, barrel)
    local modData = generator:getModData()
    modData.fuelBarrel = true
    modData.fuelBarrelItem = FuelBarrel.barrelType(barrel)
    modData.fuelBarrelLastFed = worldHours()
    GameEntityFactory.TransferComponent(fuelHolder(barrel), generator, ComponentType.FluidContainer)
    generator:transmitModData()
    FuelBarrel.track(generator)
end

function FuelBarrel.detach(generator)
    GameEntityFactory.RemoveComponentType(generator, ComponentType.FluidContainer)
    local modData = generator:getModData()
    modData.fuelBarrel = nil
    modData.fuelBarrelItem = nil
    modData.fuelBarrelLastFed = nil
    generator:transmitModData()
    FuelBarrel.refreshSprite(generator)
    tracked[generator] = nil
    pending[generator] = nil
end

function FuelBarrel.feed(generator)
    local container = FuelBarrel.getContainer(generator)
    if not container or container:isEmpty() or not container:isPureFluid(Fluid.Petrol) then return end

    local amount = math.min(generator:getMaxFuel() - generator:getFuel(), container:getAmount())
    if amount > 0 then
        container:adjustAmount(container:getAmount() - amount)
        generator:setFuel(generator:getFuel() + amount)
    end
end

-- The same hourly roll IsoGenerator:update makes, which stops once the tank is dry.
local function applyWear(generator, hours)
    local item = ScriptManager.instance:getItem(generator:getGeneratorItemType())
    local chance = item and item:getConditionLowerChance() or DEFAULT_WEAR_CHANCE
    local condition = generator:getCondition()
    for _ = 1, math.floor(hours) do
        if ZombRand(chance) == 0 then condition = condition - (ZombRand(2) + 1) end
    end
    generator:setCondition(math.max(0, condition))
end

-- If the tank couldn't cover the time away, the barrel pays the rest and restarts it.
local function recoverTimeAway(generator, entry)
    -- IsoGenerator bills whole hours, so a dry tank can show nothing unpaid by this estimate.
    local unpaid = math.max(0, entry.awayBurn - entry.tankWhenLoaded)
    entry.awayBurn = nil
    if generator:isActivated() or generator:getFuel() > 0 or generator:getCondition() <= 0 then return end

    local container = FuelBarrel.getContainer(generator)
    if not container or not container:isPureFluid(Fluid.Petrol) then return end

    local paid = math.min(unpaid, container:getAmount())
    if paid > 0 then
        container:adjustAmount(container:getAmount() - paid)
        applyWear(generator, paid / entry.burnPerHour)
    end
    if paid == unpaid and not container:isEmpty() and generator:getCondition() > 0 then
        FuelBarrel.feed(generator)
        generator:setActivated(true)
        generator:sync()
    end
end

-- An unloaded generator keeps its square and index until the chunk is saved and reused,
-- but the cell stops returning that square as soon as the chunk unloads.
local function isLoaded(generator)
    local square = generator:getSquare()
    return square ~= nil and generator:getObjectIndex() >= 0
        and getCell():getGridSquare(square:getX(), square:getY(), square:getZ()) == square
end

local function update(generator)
    FuelBarrel.feed(generator)
    generator:getModData().fuelBarrelLastFed = worldHours()
end

function FuelBarrel.feedAll()
    for generator in pairs(tracked) do
        if not isLoaded(generator) then
            tracked[generator] = nil
            pending[generator] = nil
        elseif not pending[generator] then
            -- Feeding before the first bill would change what the tank pays.
            update(generator)
        end
    end
end

function FuelBarrel.recoverAll()
    for generator, entry in pairs(pending) do
        entry.ticks = entry.ticks - 1
        if not isLoaded(generator) then
            pending[generator] = nil
        elseif entry.ticks <= 0 then
            pending[generator] = nil
            recoverTimeAway(generator, entry)
            update(generator)
        end
    end
end
