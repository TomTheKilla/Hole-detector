import numpy as np
from my_lib.types import GroupOfBlocks
from my_lib.types import Colours


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
    while (were_changes_made):
        were_changes_made = False
        for input_n in range(len(mentioned_blocks)):
            number_of_matches = 0
            last_possible_match = 1000
            for detected_n in range(len(objects)):
                if gate_matrix[input_n, detected_n]:
                    number_of_matches += 1
                    last_possible_match = detected_n

            if number_of_matches == 0 and confirmed_matches[input_n] is None:
                raise Exception(f'No matches found for {input_n + 1}. object!')  # TODO handle exeption


            elif number_of_matches == 1:
                confirmed_matches[input_n] = last_possible_match
                gate_matrix[input_n, :] = False
                gate_matrix[:, last_possible_match] = False
                were_changes_made = True
            else:
                pass

    return confirmed_matches


def AssignDescriptionsToObjects(mentioned_blocks, objects, gate_matrix, confirmed_matches):
    were_changes_made = True
    while (were_changes_made):
        were_changes_made = False
        for detected_n in range(len(objects)):
            if not (True in gate_matrix[:, detected_n]):
                continue
            number_of_matches = 0
            last_possible_match = 1000
            for input_n in range(len(mentioned_blocks)):
                if gate_matrix[input_n, detected_n]:
                    number_of_matches += 1
                    last_possible_match = input_n

            if number_of_matches == 0 and confirmed_matches[input_n] is None:
                raise Exception(f'No matches found for {input_n + 1}. object!')  # TODO handle exeption


            elif number_of_matches == 1:
                confirmed_matches[last_possible_match] = detected_n
                gate_matrix[last_possible_match, :] = False
                gate_matrix[:, detected_n] = False
                were_changes_made = True
            else:
                pass

    return confirmed_matches


def AssignAll(img_name, mentioned_blocks, objects):
    if len(mentioned_blocks) == len(objects):

        gate_matrix = CheckPossibilities(mentioned_blocks, objects)

        confirmed_matches = [None] * len(mentioned_blocks)
        confirmed_matches = AssignObjectsToDescriptions(mentioned_blocks, objects, gate_matrix, confirmed_matches)
        if None in confirmed_matches:
            confirmed_matches = AssignDescriptionsToObjects(mentioned_blocks, objects, gate_matrix, confirmed_matches)
        else:
            return confirmed_matches

        if None in confirmed_matches:  # TODO: handle exeption
            # for i, obj in enumerate(objects):
            #     cv.imwrite(f'D:/Studia/SiSW/Problems/{i}.jpg', obj.img)
            #     print(obj.blocks)
            raise Exception(f'No matching object found in {img_name}!')

        else:
            return confirmed_matches

    else:
        missing_blocks = len(mentioned_blocks) - len(objects)
        print(f'{missing_blocks} blocks not detected in {img_name}.jpg!')  # TODO: handle exception
