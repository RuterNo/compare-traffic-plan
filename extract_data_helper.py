# Functions used to extract data from element trees to a more usable format

from data_classes import *

ns = {'netex': 'http://www.netex.org.uk/netex',
      'gml': 'http://www.opengis.net/gml/3.2',
      'siri': 'http://www.siri.org.uk/siri'}


def extract_data(publication_delivery_elements):
    stop_point_in_journey_pattern_to_scheduled_stop_point_map = make_stop_point_in_journey_pattern_to_scheduled_stop_point_map(
        publication_delivery_elements)
    stop_point_in_journey_pattern_to_quay_map = make_stop_point_in_journey_pattern_to_quay_map(
        publication_delivery_elements,
        stop_point_in_journey_pattern_to_scheduled_stop_point_map)
    journey_map = extract_journey_map(publication_delivery_elements, stop_point_in_journey_pattern_to_quay_map)
    date_type_map = extract_day_type_map(publication_delivery_elements)
    blocks = extract_blocks(publication_delivery_elements, date_type_map, journey_map)
    return blocks


def find_vehicle_schedule_frame(publication_delivery_elements):
    for publication_delivery_element in publication_delivery_elements:
        vehicle_schedule_frame_element = publication_delivery_element.find('.//netex:VehicleScheduleFrame',
                                                                           namespaces=ns)
        if vehicle_schedule_frame_element is not None:
            return vehicle_schedule_frame_element
    raise ValueError("Vehicle schedule frame is missing")


def find_service_calendar_frame(publication_delivery_elements):
    for publication_delivery_element in publication_delivery_elements:
        service_calendar_frame_element = publication_delivery_element.find('.//netex:ServiceCalendarFrame',
                                                                           namespaces=ns)
        if service_calendar_frame_element is not None:
            return service_calendar_frame_element
    raise ValueError("Service calendar frame is missing")


def extract_blocks(publication_delivery_elements, date_type_map, journey_map):
    vehicle_schedule_frame_element = find_vehicle_schedule_frame(publication_delivery_elements)

    block_elements = vehicle_schedule_frame_element.findall('.//netex:Block', ns)
    blocks = []
    for block_element in block_elements:
        journey_refs = extract_journey_refs_from_block(block_element)
        journeys = []
        for journey_ref in journey_refs:
            journeys.append(journey_map[journey_ref])

        day_typ_refs = extract_day_type_refs_from_block(block_element)
        dates = []
        for day_type_ref in day_typ_refs:
            dates.append(date_type_map[day_type_ref])

        block = Block(
            block_element.attrib['id'],
            block_element.findtext('netex:PrivateCode', namespaces=ns),
            block_element.findtext("netex:StartTime", namespaces=ns),
            dates,
            journeys
        )
        blocks.append(block)
    return blocks

def extract_operating_day_map(service_calendar_frame_element):
    operating_day_elements = service_calendar_frame_element.findall('.//netex:OperatingDay', namespaces=ns)
    return {elm.attrib['id']: elm for elm in operating_day_elements}

def extract_day_type_map(publication_delivery_elements):
    service_calendar_frame_element = find_service_calendar_frame(publication_delivery_elements)

    day_type_assignment_elements = service_calendar_frame_element.findall('.//netex:DayTypeAssignment', namespaces=ns)
    operating_day_map = extract_operating_day_map(service_calendar_frame_element)
    date_map = {}
    for day_type_assignment_element in day_type_assignment_elements:
        day_type_ref_element = day_type_assignment_element.find('./netex:DayTypeRef', namespaces=ns)
        operating_day_ref_element = day_type_assignment_element.find('./netex:OperatingDayRef', namespaces=ns)
        day_type_ref = day_type_ref_element.attrib['ref']
        operating_day_ref = operating_day_ref_element.attrib['ref']
        operating_date = operating_day_map[operating_day_ref].find('./netex:CalendarDate', namespaces=ns).text
        date_map[day_type_ref] = operating_date
    return date_map


def extract_day_type_refs_from_block(block_element):
    day_type_ref_elements = block_element.findall('.//netex:DayTypeRef', namespaces=ns)
    day_type_refs = []
    for day_type_ref_element in day_type_ref_elements:
        day_type_refs.append(day_type_ref_element.attrib['ref'])
    return day_type_refs


def extract_journey_refs_from_block(block_element):
    journeys_element = block_element.find('.//netex:journeys', namespaces=ns)
    journey_refs = []
    for journey_ref_element in journeys_element:
        journey_refs.append(journey_ref_element.attrib['ref'])
    return journey_refs

def make_stop_point_in_journey_pattern_to_scheduled_stop_point_map(xml_publication_deliveries):
    journey_patterns = {}
    for xml_publication_delivery in xml_publication_deliveries:
        journey_patterns = journey_patterns | extract_stop_point_in_journeys_patterns_from_publication_delivery(
            xml_publication_delivery)
    return journey_patterns


def extract_stop_point_in_journeys_patterns_from_publication_delivery(xml_publication_delivery):
    stop_point_in_journey_pattern_elements = xml_publication_delivery.findall('.//netex:StopPointInJourneyPattern',
                                                                              namespaces=ns)
    stop_point_in_journey_pattern_map = {}
    for stop_point_in_journey_pattern_element in stop_point_in_journey_pattern_elements:
        stop_point_in_journey_pattern_id = stop_point_in_journey_pattern_element.attrib["id"]
        stop_point_ref_element = stop_point_in_journey_pattern_element.find(
            './/netex:ScheduledStopPointRef',
            namespaces=ns)
        stop_point_ref = stop_point_ref_element.attrib["ref"]
        stop_point_in_journey_pattern_map[stop_point_in_journey_pattern_id] = stop_point_ref
    return stop_point_in_journey_pattern_map


def make_stop_point_in_journey_pattern_to_quay_map(xml_publication_deliveries,
                                                   stop_point_in_journey_pattern_to_scheduled_stop_point_map):
    stop_point_in_journey_pattern_to_quay_map = {}
    passenger_stop_assignment_to_quay_map = {}
    for xml_publication_delivery in xml_publication_deliveries:
        passenger_stop_assignment_elements = xml_publication_delivery.findall('.//netex:PassengerStopAssignment',
                                                                              namespaces=ns)
        for passenger_stop_assignment_element in passenger_stop_assignment_elements:
            quay_ref = passenger_stop_assignment_element.find('.//netex:QuayRef', namespaces=ns).attrib["ref"]
            scheduled_stop_point_ref = \
                passenger_stop_assignment_element.find('.//netex:ScheduledStopPointRef', namespaces=ns).attrib["ref"]
            passenger_stop_assignment_to_quay_map[scheduled_stop_point_ref] = quay_ref
    for stop_point_in_journey_pattern_ref in stop_point_in_journey_pattern_to_scheduled_stop_point_map:
        passenger_stop_assignment_ref = stop_point_in_journey_pattern_to_scheduled_stop_point_map[
            stop_point_in_journey_pattern_ref]
        stop_point_in_journey_pattern_to_quay_map[stop_point_in_journey_pattern_ref] = \
            passenger_stop_assignment_to_quay_map[passenger_stop_assignment_ref]
    return stop_point_in_journey_pattern_to_quay_map


def extract_journey_map(xml_publication_deliveries, journey_pattern_point_map):
    journeys = []
    for xml_publication_delivery in xml_publication_deliveries:
        journeys += extract_journeys_from_publication_delivery(xml_publication_delivery, journey_pattern_point_map)
    journey_map = {}
    for journey in journeys:
        journey_map[journey.id] = journey
    return journey_map


def extract_journeys_from_publication_delivery(xml_publication_delivery, journey_pattern_point_map):
    journey_elements = xml_publication_delivery.findall('.//netex:ServiceJourney', namespaces=ns) + \
                       xml_publication_delivery.findall('.//netex:DeadRun', namespaces=ns)
    journeys = []
    for journey_element in journey_elements:
        stops = extract_stops_from_journey(journey_element, journey_pattern_point_map)
        journey = Journey(
            journey_element.attrib["id"],
            stops
        )
        journeys.append(journey)
    return journeys


def extract_stops_from_journey(journey_element, stop_point_in_journey_pattern_to_quay_map):
    timetabled_passing_time_elements = journey_element.findall('.//netex:TimetabledPassingTime', namespaces=ns)
    stops = []
    for timetabled_passing_time_element in timetabled_passing_time_elements:
        stop_point_in_journey_pattern_ref_element = timetabled_passing_time_element.find(
            './/netex:StopPointInJourneyPatternRef',
            namespaces=ns)
        stop_point_in_journey_pattern_ref = stop_point_in_journey_pattern_ref_element.attrib['ref']
        quay_id = stop_point_in_journey_pattern_to_quay_map[stop_point_in_journey_pattern_ref]

        stop = Stop(
            quay_id,
            timetabled_passing_time_element.findtext('.//netex:DepartureTime', namespaces=ns)
        )
        stops.append(stop)
    return stops
