-- Runs FuelBarrel.lua through unload and reload cycles against a model of IsoGenerator's billing.
-- Run from the mod folder: luajit tests/test_unload.lua
local H = dofile((os.getenv("TPCORE") or "../_tpcore") .. "/tests/harness.lua")
local now = 1000
local cellSquares = {}
Events = setmetatable({}, { __index = function() return { Add = function() end } end })
Fluid = { Petrol = "petrol" }
ComponentType = { FluidContainer = "fluid" }
FluidFilter = { new = function() return { setFilterType = function() end, add = function() end } end, FilterType = {} }
GameEntityFactory = { TransferComponent = function() end }
instanceof = function() return false end
getGameTime = function() return { getWorldAgeHours = function() return now end } end
getCell = function() return { getGridSquare = function() return cellSquares[1] end } end
ScriptManager = { instance = { getItem = function() return { getConditionLowerChance = function() return 30 end } end } }
ZombRand = function(n) return math.random(0, n - 1) end
dofile("42/media/lua/shared/FuelBarrel.lua")

local BURN = 0.5 -- litres per hour
local FRAMES_PER_MINUTE = 4

local check = H.check

local function newContainer()
    local c = { amount = 0 }
    function c:isEmpty() return self.amount <= 0 end
    function c:isPureFluid() return self.amount > 0 end
    function c:getAmount() return self.amount end
    function c:adjustAmount(a) self.amount = a end
    function c:setWhitelist() end
    return c
end

-- A generator object as the engine builds it from the saved state, on a square of its own.
local function newGenerator(state)
    local square = { getX = function() return 0 end, getY = function() return 0 end, getZ = function() return 0 end }
    cellSquares[1] = square
    local g = { s = state }
    function g:getModData() return self.s.modData end
    function g:getComponent() return self.s.container end
    function g:getSprite() return { getName = function() return "appliances_misc_01_0" end } end
    function g:setOverlaySprite() end
    function g:getSquare() return square end
    function g:getObjectIndex() return 0 end -- unloaded objects keep it until the chunk is reused
    function g:isActivated() return self.s.activated end
    function g:setActivated(v) self.s.activated = v; if v then self.s.lastHour = math.floor(now) end end
    function g:getFuel() return self.s.fuel end
    function g:setFuel(f) self.s.fuel = f end
    function g:getMaxFuel() return 10 end
    function g:getTotalPowerUsing() return BURN end
    function g:getCondition() return 100 end
    function g:setCondition() end
    function g:getGeneratorItemType() return "Base.Generator" end
    function g:sync() end
    function g:transmitModData() end
    -- IsoGenerator.update: bills whole hours and switches off when the tank is dry.
    function g:update()
        if not self.s.activated then return end
        for _ = 1, math.floor(now) - self.s.lastHour do
            self.s.fuel = self.s.fuel - BURN
            if self.s.fuel <= 0 then self.s.fuel = 0; self:setActivated(false); break end
        end
        self.s.lastHour = math.floor(now)
    end
    return g
end

-- One frame in engine order: the generator bills itself, then OnTick, then EveryOneMinute on the minute.
local function runLoaded(g, minutes)
    for _ = 1, minutes do
        for frame = 1, FRAMES_PER_MINUTE do
            now = now + 1 / 60 / FRAMES_PER_MINUTE
            g:update()
            FuelBarrel.recoverAll()
            if frame == FRAMES_PER_MINUTE then FuelBarrel.feedAll() end
        end
    end
end

-- Steps alternate between loaded minutes and hours away. Returns litres used, litres it should
-- have used running the whole time, and whether it ends up running.
local function play(steps)
    now = 1000
    local state = { modData = {}, container = newContainer(), activated = true, fuel = 10, lastHour = 1000 }
    local g = newGenerator(state)
    FuelBarrel.attach(g, { getFullType = function() return "FuelBarrel.FuelBarrel" end })
    state.container.amount = 100
    local start, hours = 110, 0
    for _, step in ipairs(steps) do
        if step.loaded then
            runLoaded(g, step.loaded)
            hours = hours + step.loaded / 60
        else
            cellSquares[1] = nil -- unloaded: the cell no longer returns its square
            now = now + step.away
            hours = hours + step.away
            g = newGenerator(state)
            FuelBarrel.track(g)
        end
    end
    return start - (state.fuel + state.container.amount), math.min(start, hours * BURN), state.activated
end

local function close(a, b) return math.abs(a - b) < 1 end

local used, should, running = play({ { loaded = 5 }, { away = 10 }, { loaded = 5 } })
check("away 10 h: the tank covers it", close(used, should) and running)
used, should, running = play({ { loaded = 5 }, { away = 60 }, { loaded = 5 } })
check("away 60 h: the barrel pays the rest and restarts it", close(used, should) and running)
used, should, running = play({ { loaded = 5 }, { away = 300 }, { loaded = 5 } })
check("away 300 h: it all runs out and stays off", close(used, should) and not running)
used, should, running = play({ { loaded = 5 }, { away = 60 }, { loaded = 1 }, { away = 60 }, { loaded = 5 } })
check("back for a minute between long absences: still running, billed once", close(used, should) and running)
used, should, running = play({ { loaded = 5 }, { away = 10 }, { loaded = 1 }, { away = 10 }, { loaded = 5 } })
check("back for a minute between short absences: billed once", close(used, should) and running)

-- An unloaded generator still has its square and index, but must not be fed.
now = 1000
local state = { modData = {}, container = newContainer(), activated = true, fuel = 10, lastHour = 1000 }
local stale = newGenerator(state)
FuelBarrel.attach(stale, { getFullType = function() return "FuelBarrel.FuelBarrel" end })
state.container.amount = 50
state.fuel = 5
cellSquares[1] = nil
FuelBarrel.feedAll()
check("an unloaded generator isn't fed", state.fuel == 5 and state.container.amount == 50)

H.done()
