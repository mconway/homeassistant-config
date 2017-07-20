home = 0
for entity_id in hass.states.entity_ids('group.people'):
    logger.info("Got Entity: %s" % entity_id)
    state = hass.states.get(entity_id)
    if state.state == 'home':
        home = home + 1

hass.states.set('sensor.people_home', home, {
    'unit_of_measurement': 'people',
    'friendly_name': 'People home'
})