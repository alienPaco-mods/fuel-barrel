require "TimedActions/ISBaseTimedAction"
require "TimedActions/ISTakeGenerator"
require "FuelBarrel"

-- Connects a barrel to a generator with a hose, or disconnects it and returns both.
-- Either way takes pliers, which are kept.
ISFuelBarrelHose = ISBaseTimedAction:derive("ISFuelBarrelHose")

local CONNECT_TIME = 150

function ISFuelBarrelHose:isValid()
    if self.generator:getObjectIndex() == -1 then return false end
    if not self.pliers:isInPlayerInventory() or self.pliers:isBroken() then return false end
    if self.barrel then
        local barrelThere
        if FuelBarrel.isOnGround(self.barrel) then
            barrelThere = self.barrel:getWorldObjectIndex() ~= -1
        else
            barrelThere = self.barrel:isInPlayerInventory()
        end
        return barrelThere and self.hose:isInPlayerInventory()
            and not FuelBarrel.isAttached(self.generator)
            and FuelBarrel.holdsOnlyFuel(FuelBarrel.barrelContainer(self.barrel))
    end
    return FuelBarrel.isAttached(self.generator) and FuelBarrel.getContainer(self.generator):isEmpty()
end

function ISFuelBarrelHose:waitToStart()
    self.character:faceThisObject(self.generator)
    return self.character:shouldBeTurning()
end

function ISFuelBarrelHose:update()
    self.character:faceThisObject(self.generator)
    self.character:setMetabolicTarget(Metabolics.MediumWork)
end

function ISFuelBarrelHose:start()
    self:setActionAnim("Loot")
    self.character:SetVariable("LootPosition", "Low")
    self.character:reportEvent("EventLootItem")
end

function ISFuelBarrelHose:perform()
    ISBaseTimedAction.perform(self)
end

function ISFuelBarrelHose:complete()
    local inventory = self.character:getInventory()
    if self.barrel then
        FuelBarrel.attach(self.generator, self.barrel)
        local used = { self.hose }
        if FuelBarrel.isOnGround(self.barrel) then
            self.barrel:getSquare():transmitRemoveItemFromSquare(self.barrel)
            triggerEvent("OnContainerUpdate")
        else
            table.insert(used, self.barrel)
        end
        for _, item in ipairs(used) do
            item:getContainer():Remove(item)
            sendRemoveItemFromContainer(inventory, item)
        end
    else
        local barrelItem = FuelBarrel.typeOf(self.generator).item
        -- A fresh item has the script's size, not the one the barrel was crafted with.
        local capacity = FuelBarrel.getContainer(self.generator):getCapacity()
        FuelBarrel.detach(self.generator)
        local barrel = inventory:AddItem(barrelItem)
        barrel:getFluidContainer():setCapacity(capacity)
        sendAddItemToContainer(inventory, barrel)
        sendAddItemToContainer(inventory, inventory:AddItem(FuelBarrel.HOSE))
    end
    return true
end

function ISFuelBarrelHose:getDuration()
    if self.character:isTimedActionInstant() then return 1 end
    return CONNECT_TIME
end

-- Pass a barrel (carried, or lying by the generator) and a hose to connect, or neither to disconnect.
function ISFuelBarrelHose:new(character, generator, pliers, barrel, hose)
    local o = ISBaseTimedAction.new(self, character)
    o.generator = generator
    o.barrel = barrel
    o.hose = hose
    o.pliers = pliers
    o.maxTime = o:getDuration()
    return o
end

-- A generator carries its barrel's container, so it must be disconnected before it is picked up.
local vanillaTakeIsValid = ISTakeGenerator.isValid

function ISTakeGenerator:isValid()
    return not FuelBarrel.isAttached(self.generator) and vanillaTakeIsValid(self)
end
