# Functions used to compare blocks

def compare_blocks(blocks_1, blocks_2, file_1, file_2):
    errors = []
    for block_1 in blocks_1:
        matching_block = None
        for block_2 in blocks_2:
            if blocks_are_matching(block_1, block_2):
                matching_block = block_2
                break
        if matching_block is None:
            errors.append(make_match_not_found_message(block_1, file_1, file_2))
        else:
            errors_for_block = compare_two_blocks(block_1, matching_block, file_1, file_2)
            errors += errors_for_block
    for block_2 in blocks_2:
        matching_block = None
        for block_1 in blocks_1:
            if blocks_are_matching(block_1, block_2):
                matching_block = block_1
                break
        if matching_block is None:
            errors.append(make_match_not_found_message(block_2, file_2, file_1))
    return errors


def compare_two_blocks(block_1, block_2, file_1, file_2):
    errors = []
    if len(block_1.journeys) != len(block_2.journeys):
        errors.append(f'Different number of journeys on block {block_1.id}')
        return errors
    for journey_index, (journey_1, journey_2) in enumerate(zip(block_1.journeys, block_2.journeys)):
        errors += compare_journeys(journey_1, journey_2, block_1.id, journey_index + 1)
    return errors


def compare_journeys(journey_1, journey_2, block_id, journey_index):
    errors = []
    if len(journey_1.stops) != len(journey_2.stops):
        errors.append(f'Different number of stops for journey {journey_index} in block {block_id}')
        return errors
    for stop_index, (stop_1, stop_2) in enumerate(zip(journey_1.stops, journey_2.stops)):
        errors += compare_stops(stop_1, stop_2, block_id, journey_index, stop_index + 1)
    return errors


def compare_stops(stop_1, stop_2, block_id, journey_index, stop_index):
    errors = []
    if stop_1.departure_time != stop_2.departure_time:
        errors.append(f'Different departure time on stop {stop_index} on journey {journey_index} in block {block_id}')
    if stop_1.quay != stop_2.quay:
        errors.append(f'Different quay on stop {stop_index} on journey {journey_index} in block {block_id}')
    return errors

def blocks_are_matching(block_1, block_2):
    return block_1.start_time == block_2.start_time and block_1.vehicle_task_id == block_2.vehicle_task_id


def make_match_not_found_message(block, file_with_block, file_without_block):
    return f'File {file_with_block} contains a block with vehicle task id {block.vehicle_task_id} and start time ' + \
           f'{block.start_time}. No matching block was found in file {file_without_block}. Block id: {block.id}'
