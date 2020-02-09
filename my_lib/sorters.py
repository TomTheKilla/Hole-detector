import numpy as np
import cv2  as cv
from my_lib.types import GroupOfBlocks
from my_lib.types import Colours
from my_lib import detectors


def CheckPossibilities(mentioned_blocks, objects):
    gate_matrix = np.zeros((len(mentioned_blocks), len(mentioned_blocks)), bool)

    for input_n, input in enumerate(mentioned_blocks):
        for detected_n, detected in enumerate(objects):
            possible = False

            # For each colour check if there were any blocks detected
            for colour in Colours:
                current_colour = colour.name
                if int(input.get(current_colour)) >= detected.blocks.get(current_colour):
                    possible = True
                else:
                    possible = False
                    break

            gate_matrix[input_n, detected_n] = possible

    return gate_matrix


def AssignObjectsToDescriptions(mentioned_blocks, objects, gate_matrix, confirmed_matches):
    were_changes_made = True
    not_matched_descriptions = []
    while (were_changes_made):
        were_changes_made = False
        for input_n in range(len(mentioned_blocks)):
            if not (True in gate_matrix[input_n, :]):
                if confirmed_matches[input_n] is None:
                    if input_n not in not_matched_descriptions:
                        not_matched_descriptions.append(input_n)
                continue
            number_of_matches = 0
            last_possible_match = 1000
            for detected_n in range(len(objects)):
                if gate_matrix[input_n, detected_n]:
                    number_of_matches += 1
                    last_possible_match = detected_n

            if number_of_matches == 1:
                confirmed_matches[input_n] = last_possible_match
                objects[last_possible_match].description = input_n
                gate_matrix[:, last_possible_match] = False
                were_changes_made = True
            else:
                pass

    if len(not_matched_descriptions) == 1:
        descript = not_matched_descriptions[0]
        [obj] = [n_obj for n_obj in range(len(objects)) if n_obj not in confirmed_matches]
        confirmed_matches[descript] = obj
        objects[obj].description = descript

    return confirmed_matches, gate_matrix


def AssignDescriptionsToObjects(mentioned_blocks, objects, gate_matrix, confirmed_matches):
    were_changes_made = True
    not_matched_objects = []
    while (were_changes_made):
        were_changes_made = False
        for detected_n in range(len(objects)):
            if not (True in gate_matrix[:, detected_n]):
                if detected_n not in confirmed_matches:
                    if detected_n not in not_matched_objects:
                        not_matched_objects.append(detected_n)
                continue
            number_of_matches = 0
            last_possible_match = 1000
            for input_n in range(len(mentioned_blocks)):
                if gate_matrix[input_n, detected_n]:
                    number_of_matches += 1
                    last_possible_match = input_n

            if number_of_matches == 1:
                confirmed_matches[last_possible_match] = detected_n
                objects[detected_n].description = last_possible_match
                gate_matrix[last_possible_match, :] = False
                were_changes_made = True
            else:
                pass

        if len(not_matched_objects) == 1:
            obj = not_matched_objects[0]
            [descript] = [i for i, x in enumerate(confirmed_matches) if x is None]
            confirmed_matches[descript] = obj
            objects[obj].description = descript

    return confirmed_matches, gate_matrix


def DecideBasedOnArea(mentioned_blocks, objects, gate_matrix, confirmed_matches):
    # find all descriptions that hasn't been assigned yet
    not_assigned_descriptions = [i for i, x in enumerate(confirmed_matches) if x is None]

    # for every not assigned description find which objects compete for it
    competing_objects = []
    for pos in not_assigned_descriptions:
        competing_objects.append([i for i, x in enumerate(gate_matrix[pos, :]) if x])

    possible_descriptions_for_objects = []
    for pos in range(len(objects)):
        possible = [i for i, x in enumerate(gate_matrix[:, pos]) if x]
        possible_descriptions_for_objects.append(possible)

    for competition, n_description in enumerate(not_assigned_descriptions):
        description = mentioned_blocks[n_description]
        competitors = competing_objects[competition]  # TODO remove identical cometitions after

        # Find single competing description
        descriptions = possible_descriptions_for_objects[competitors[0]]
        for desc in descriptions:
            if desc != description:
                competing_description = mentioned_blocks[desc]
        n_of_blocks_in_description = []
        for colour in Colours:
            n = int(description[colour.name])
            n_of_blocks_in_description.append(n)

        description_colours_present = [i for i, x in enumerate(n_of_blocks_in_description) if (x != 0)]

        n_of_blocks_in_competing_description = []
        for colour in Colours:
            n = int(competing_description[colour.name])
            n_of_blocks_in_competing_description.append(n)

        competing_description_colours_present = [i for i, x in enumerate(n_of_blocks_in_competing_description) if
                                                 (x != 0)]

        # Find differences between descriptions
        missing_colours_from_description = [item for item in competing_description_colours_present if
                                            item not in description_colours_present]
        additional_colours_in_description = [item for item in description_colours_present if
                                             item not in competing_description_colours_present]

        # Select colour to look for in images that would differentiate them
        if len(missing_colours_from_description) != 0:
            target_colour = Colours(missing_colours_from_description[0])
            [target_description] = [x for x in descriptions if x != n_description]
        elif len(additional_colours_in_description) != 0:
            target_colour = Colours(additional_colours_in_description[0])
            target_description = n_description
        else:
            diff = [abs(i - j) for i, j in zip(n_of_blocks_in_description, n_of_blocks_in_competing_description)]
            biggest_diff = 0
            target_colour = None
            for i, x in enumerate(diff):
                if x > biggest_diff:
                    target_colour = i
                    biggest_diff = x

            if n_of_blocks_in_description[target_colour] > n_of_blocks_in_competing_description[target_colour]:
                target_colour = Colours(target_colour)
                target_description = n_description
            else:
                target_colour = Colours(target_colour)
                [target_description] = [x for x in descriptions if x != n_description]


        leader = None
        top_area_ratio = 0.0
        for pos, competitor in enumerate(competitors):
            # find area of object
            obj_area = objects[competitor].total_area
            # find area of target colour
            colour_area = objects[competitor].ColourArea(target_colour)
            # compare with previous
            ratio = colour_area / obj_area
            if top_area_ratio < ratio:
                leader = pos
                top_area_ratio = ratio

        if leader is not None:
            # treat leader as confirmed match for given description
            confirmed_matches[target_description] = competitors[leader]
            objects[competitors[leader]].description = target_description
            # update gate_matrix
            gate_matrix[target_description, :] = False
            gate_matrix[:, competitors[leader]] = False

            # TODO if one none it should be straigh forward but the next function should do

            # check if rest of the objects can be assigned
            confirmed_matches, gate_matrix = AssignObjectsToDescriptions(mentioned_blocks, objects, gate_matrix,
                                                                         confirmed_matches)

            if None in confirmed_matches:
                confirmed_matches, gate_matrix = AssignDescriptionsToObjects(mentioned_blocks, objects, gate_matrix,
                                                                             confirmed_matches)
            else:
                return confirmed_matches

        else:
            # TODO handle
            pass

    return confirmed_matches, gate_matrix


def Assign(img_name, img, mentioned_blocks, objects):
    if len(mentioned_blocks) > len(objects):

        # read image and black out all known objects
        temp = img.copy()
        for obj in objects:
            box = obj.bbox
            cv.drawContours(temp, [box], 0, (0, 0, 0), cv.FILLED)

        # find all circles that are left
        circles, test = detectors.AdaptiveHoughCirlces(temp)

        # if only one object missing append it otherwise use mean shift to try to guess
        if len(mentioned_blocks) - len(objects) == 1:
            blocks = {
                'red': 0,
                'blue': 0,
                'white': 0,
                'grey': 0,
                'yellow': 0,
            }

            obj = GroupOfBlocks(img_name, temp, None, None, None)
            obj.blocks = blocks
            obj.holes = circles[0, :]
            obj.n_holes = len(circles[0, :])
            objects.append(obj)

        else:
            pass
            # TODO meanshift
    elif len(mentioned_blocks) < len(objects):
        return None

    gate_matrix = CheckPossibilities(mentioned_blocks, objects)

    confirmed_matches = [None] * len(mentioned_blocks)
    confirmed_matches, gate_matrix = AssignObjectsToDescriptions(mentioned_blocks, objects, gate_matrix,
                                                                 confirmed_matches)
    if None in confirmed_matches:
        confirmed_matches, gate_matrix = AssignDescriptionsToObjects(mentioned_blocks, objects, gate_matrix,
                                                                     confirmed_matches)
    else:
        return confirmed_matches

    if None in confirmed_matches:
        confirmed_matches = DecideBasedOnArea(mentioned_blocks, objects, gate_matrix, confirmed_matches)
    else:
        return confirmed_matches

    if None in confirmed_matches:
        # Find all not assigned objects and descriptions
        desc = [i for i, x in enumerate(confirmed_matches) if x is None]
        objs = [x for x in range(len(mentioned_blocks)) if x not in confirmed_matches]
        # assign them randomly
        for i, x in enumerate(desc):
            confirmed_matches[desc] = objs[i]

    else:
        return confirmed_matches
