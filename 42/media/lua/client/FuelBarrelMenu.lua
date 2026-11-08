-- Fuel Barrel B42: right-click options on generators, and the barrel level in the info window.
require "ISUI/ISGeneratorInfoWindow"
require "FuelBarrel"
require "TimedActions/ISFuelBarrelHose"

local function findGenerator(worldobjects)
    for _, object in ipairs(worldobjects) do
        local square = object:getSquare()
        local objects = square and square:getObjects()
        for i = 0, objects and objects:size() - 1 or -1 do
            if instanceof(objects:get(i), "IsoGenerator") then return objects:get(i) end
        end
    end
end

local function disable(option, tooltipKey)
    option.notAvailable = true
    local tooltip = ISWorldObjectContextMenu.addToolTip()
    tooltip.description = getText(tooltipKey)
    option.toolTip = tooltip
end

local function onConnect(player, generator, barrel, hose, pliers)
    local playerObj = getSpecificPlayer(player)
    if luautils.walkAdj(playerObj, generator:getSquare()) then
        if not FuelBarrel.isOnGround(barrel) then ISInventoryPaneContextMenu.transferIfNeeded(playerObj, barrel) end
        ISInventoryPaneContextMenu.transferIfNeeded(playerObj, hose)
        ISInventoryPaneContextMenu.transferIfNeeded(playerObj, pliers)
        ISTimedActionQueue.add(ISFuelBarrelHose:new(playerObj, generator, pliers, barrel, hose))
    end
end

local function onDisconnect(player, generator, pliers)
    local playerObj = getSpecificPlayer(player)
    if luautils.walkAdj(playerObj, generator:getSquare()) then
        ISInventoryPaneContextMenu.transferIfNeeded(playerObj, pliers)
        ISTimedActionQueue.add(ISFuelBarrelHose:new(playerObj, generator, pliers))
    end
end

-- Vanilla nests some options in submenus, so this looks one level down as well.
local function findOption(context, name)
    local option = context:getOptionFromName(name)
    if option then return option, context end

    for _, entry in ipairs(context.options) do
        local subMenu = entry.subOption and context:getSubMenu(entry.subOption)
        option = subMenu and subMenu:getOptionFromName(name)
        if option then return option, subMenu, entry end
    end
end

local function barrelIcon(barrelType)
    return ScriptManager.instance:getItem(barrelType.item):getNormalTexture()
end

local function barrelText(barrelType, suffix)
    return getText("ContextMenu_" .. barrelType.textKey .. (suffix or ""))
end

local function addConnectOption(player, context, generator)
    local inventory = getSpecificPlayer(player):getInventory()
    local hose = inventory:getFirstTypeRecurse(FuelBarrel.HOSE)
    local pliers = FuelBarrel.findPliers(inventory)

    local menus = { context }
    local _, generatorMenu = findOption(context, getText("ContextMenu_GeneratorInfo"))
    if generatorMenu and generatorMenu ~= context then table.insert(menus, generatorMenu) end

    for _, barrelType in ipairs(FuelBarrel.TYPES) do
        -- One you carry comes first, then one lying by the generator.
        local barrel = inventory:getFirstTypeRecurse(barrelType.item) or FuelBarrel.findGroundBarrel(generator, barrelType.item)
        for _, menu in ipairs(barrel and menus or {}) do
            local option = menu:addOption(barrelText(barrelType, "_Connect"), player, onConnect, generator, barrel, hose, pliers)
            option.iconTexture = barrelIcon(barrelType)
            if not hose then
                disable(option, "ContextMenu_FuelBarrel_NeedHose")
            elseif not pliers then
                disable(option, "ContextMenu_FuelBarrel_NeedPliers")
            elseif not FuelBarrel.holdsOnlyFuel(FuelBarrel.barrelContainer(barrel)) then
                disable(option, "ContextMenu_FuelBarrel_NotFuel")
            end
        end
    end
end

local function addAttachedOptions(player, context, generator)
    local container = FuelBarrel.getContainer(generator)
    local barrelType = FuelBarrel.typeOf(generator)

    -- Vanilla already lists the barrel's fluid options, labelled with the generator's name.
    -- It only lists one object's, so the menu found here can belong to something nearby.
    local info, fluidMenu, fluidEntry = findOption(context, getText("Fluid_Show_Info"))
    if fluidEntry and info.param1 == container then
        fluidEntry.name = barrelText(barrelType)
        fluidEntry.iconTexture = barrelIcon(barrelType)
        fluidEntry.itemForTexture = nil
    else
        fluidMenu = context
        context:addOption(barrelText(barrelType, "_Transfer"), player, ISWorldObjectContextMenu.onFluidTransfer, container)
    end

    local pliers = FuelBarrel.findPliers(getSpecificPlayer(player):getInventory())
    local option = fluidMenu:addOption(barrelText(barrelType, "_Disconnect"), player, onDisconnect, generator, pliers)
    if not container:isEmpty() then
        disable(option, "ContextMenu_FuelBarrel_HasFuel")
    elseif not pliers then
        disable(option, "ContextMenu_FuelBarrel_NeedPliers")
    end

    local take = findOption(context, getText("ContextMenu_GeneratorTake"))
    if take then disable(take, "ContextMenu_FuelBarrel_DisconnectFirst") end
end

local function onFillMenu(player, context, worldobjects, test)
    if test then return end
    local generator = findGenerator(worldobjects)
    if not generator then return end

    if FuelBarrel.isAttached(generator) then
        addAttachedOptions(player, context, generator)
    else
        addConnectOption(player, context, generator)
    end
end

Events.OnFillWorldObjectContextMenu.Add(onFillMenu)

local vanillaGetRichText = ISGeneratorInfoWindow.getRichText

function ISGeneratorInfoWindow.getRichText(object, displayStats)
    local text = vanillaGetRichText(object, displayStats)
    if displayStats and FuelBarrel.isAttached(object) then
        local container = FuelBarrel.getContainer(object)
        local name = barrelText(FuelBarrel.typeOf(object))
        local level = getText("IGUI_FuelBarrel_Level", name, math.floor(container:getAmount()), math.floor(container:getCapacity()))
        text = level .. " <LINE> " .. text
    end
    return text
end
