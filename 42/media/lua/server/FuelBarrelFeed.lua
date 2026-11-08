-- Fuel Barrel B42: runs the barrel-to-tank feed and picks generators back up on load.
if isClient() then return end

require "FuelBarrel"

local MAP_PRIORITY = 5

Events.EveryOneMinute.Add(FuelBarrel.feedAll)
Events.OnTick.Add(FuelBarrel.recoverAll)

for _, sprite in ipairs(FuelBarrel.generatorSprites()) do
    MapObjects.OnLoadWithSprite(sprite, FuelBarrel.track, MAP_PRIORITY)
end
