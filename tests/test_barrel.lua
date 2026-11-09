-- Checks the barrel rules outside the game. Run from the mod folder: luajit tests/test_barrel.lua
local H = dofile((os.getenv("TPCORE") or "../_tpcore") .. "/tests/harness.lua")
Events = setmetatable({}, { __index = function() return { Add = function() end } end })
Fluid = { Petrol = "petrol" }
ComponentType = { FluidContainer = "fluid" }
dofile("42/media/lua/shared/FuelBarrel.lua")

local check = H.check

local function barrel(fullType)
    local item = { capacity = 0 }
    function item:getFullType() return fullType end
    function item:getFluidContainer()
        return { setCapacity = function(_, value) item.capacity = value end }
    end
    return item
end

local function crafted(item)
    local data = {}
    function data:getAllCreatedItems()
        return { size = function() return 1 end, get = function() return item end }
    end
    FuelBarrel.onCreateBarrel(data)
    return item
end

check("a standard barrel holds 120", crafted(barrel("FuelBarrel.FuelBarrel")).capacity == 120)
check("a crude one 60", crafted(barrel("FuelBarrel.CrudeFuelBarrel")).capacity == 60)
SandboxVars = { FuelBarrel = { Capacity = 200, CrudeCapacity = 90 } }
check("the sandbox sets each size", crafted(barrel("FuelBarrel.FuelBarrel")).capacity == 200 and crafted(barrel("FuelBarrel.CrudeFuelBarrel")).capacity == 90)
check("other outputs are left alone", crafted(barrel("Base.Plank")).capacity == 0)

local script = io.open("42/media/scripts/FuelBarrel.txt"):read("*a")
check("the script's sizes match the defaults", script:find("Capacity = 120.0", 1, true) and script:find("Capacity = 60.0", 1, true))

local function generator(data, container)
    return { getModData = function() return data end, getComponent = function() return container end }
end
check("an attached generator is seen", FuelBarrel.isAttached(generator({ fuelBarrel = true }, {})))
check("and a bare one isn't", not FuelBarrel.isAttached(generator({})))
check("nor one whose barrel container is gone", not FuelBarrel.isAttached(generator({ fuelBarrel = true })))
check("an old barrel counts as standard", FuelBarrel.typeOf(generator({})) == FuelBarrel.TYPES[1])
check("a crude one is remembered", FuelBarrel.typeOf(generator({ fuelBarrelItem = "FuelBarrel.CrudeFuelBarrel" })) == FuelBarrel.TYPES[2])

local function container(empty, pure)
    return { isEmpty = function() return empty end, isPureFluid = function() return pure end }
end
check("an empty barrel counts as fuel", FuelBarrel.holdsOnlyFuel(container(true, false)))
check("so does pure petrol", FuelBarrel.holdsOnlyFuel(container(false, true)))
check("but not a mix", not FuelBarrel.holdsOnlyFuel(container(false, false)))

-- Barrels lying by the generator
local squares = {}
getCell = function() return { getGridSquare = function(_, x, y) return squares[x .. "," .. y] end } end
instanceof = function(object, class) return class == "IsoWorldInventoryObject" and object.onGround == true end
local function square(x, y, worldItems)
    local sq = { getX = function() return x end, getY = function() return y end, getZ = function() return 0 end }
    function sq:getWorldObjects() return { size = function() return #worldItems end, get = function(_, i) return worldItems[i + 1] end } end
    squares[x .. "," .. y] = sq
    return sq
end
local function onGround(fullType, componentOnObject)
    local tank = { name = "tank" }
    local item = { getFullType = function() return fullType end, getComponent = function() return not componentOnObject and tank or nil end }
    return { onGround = true, getItem = function() return item end, getComponent = function() return componentOnObject and tank or nil end }, tank
end
local crude, crudeTank = onGround("FuelBarrel.CrudeFuelBarrel", true)
local far = onGround("FuelBarrel.FuelBarrel", true)
local genSquare = square(10, 10, {})
square(11, 9, { onGround("Base.Plank", true), crude })
square(12, 10, { far })
local gen = { getSquare = function() return genSquare end }
check("a barrel next to the generator is found", FuelBarrel.findGroundBarrel(gen, "FuelBarrel.CrudeFuelBarrel") == crude)
check("but not one two squares away", FuelBarrel.findGroundBarrel(gen, "FuelBarrel.FuelBarrel") == nil)
check("a ground barrel's type is its item's", FuelBarrel.barrelType(crude) == "FuelBarrel.CrudeFuelBarrel")
check("its fuel is on the ground object after a drop", FuelBarrel.barrelContainer(crude) == crudeTank)
local older, olderTank = onGround("FuelBarrel.FuelBarrel", false)
check("or still on the item if it never moved", FuelBarrel.barrelContainer(older) == olderTank)
local carried = { getFullType = function() return "FuelBarrel.FuelBarrel" end, getComponent = function() return "carried" end }
check("a carried barrel is not on the ground", not FuelBarrel.isOnGround(carried) and FuelBarrel.barrelContainer(carried) == "carried")

H.done()
