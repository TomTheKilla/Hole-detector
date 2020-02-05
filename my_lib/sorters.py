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
                pass
                # raise Exception(f'No matches found for {input_n + 1}. object!')  # TODO handle exeption


            elif number_of_matches == 1:
                confirmed_matches[input_n] = last_possible_match
                gate_matrix[input_n, :] = False
                gate_matrix[:, last_possible_match] = False
                were_changes_made = True
            else:
                pass

    return confirmed_matches, gate_matrix


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

    return confirmed_matches, gate_matrix


def FindMissing(mentioned_blocks, objects, gate_matrix, confirmed_matches):
    # find all descriptions that hasn't been assigned yet
    positions_of_descriptions = [i for i, x in enumerate(confirmed_matches) if x is None]

    # for every not assigned description find which objects compete for it
    competing_objects = []
    for pos in positions_of_descriptions:
        competing_objects.append([i for i, x in enumerate(gate_matrix[pos, :]) if x is True])

    # # find with which objects and for what description are competing
    # contests = []
    # for i, contestant_a in enumerate(competing_objects):
    #     for j, contestant_b in enumerate(competing_objects):
    #         if i != j:
    #             descriptions = list(set(contestant_a).intersection(contestant_b))
    #             if len(descriptions) != 0:
    #                 contest = [descriptions, i, j]
    #                 contests.append(contest)
    #         else:
    #             # object can't compete with itself
    #             continue

    #
    n_multiway_contest = 0
    for n_description, contest in enumerate(competing_objects):
        if len(contest) == 2:
            description = mentioned_blocks[positions_of_descriptions[n_description]]


        if len(contest) >2:
            n_multiway_contest += 1
            continue

        else:
            print('Not supposed to happen!')    # TODO handle this

    return confirmed_matches, gate_matrix


def AssignAll(img_name, mentioned_blocks, objects):
    if len(mentioned_blocks) == len(objects):

        gate_matrix = CheckPossibilities(mentioned_blocks, objects)

        confirmed_matches = [None] * len(mentioned_blocks)
        confirmed_matches, gate_matrix = AssignObjectsToDescriptions(mentioned_blocks, objects, gate_matrix,
                                                                     confirmed_matches)
        if None in confirmed_matches:
            confirmed_matches, gate_matrix = AssignDescriptionsToObjects(mentioned_blocks, objects, gate_matrix,
                                                                         confirmed_matches)
        else:
            return confirmed_matches

        # if None in confirmed_matches:
        #     confirmed_matches, gate_matrix = FindMissing(mentioned_blocks, objects, gate_matrix, confirmed_matches)
        # else:
        #     return confirmed_matches

        if None in confirmed_matches:  # TODO: handle exeption
            # for i, obj in enumerate(objects):
            #     cv.imwrite(f'D:/Studia/SiSW/Problems/{i}.jpg', obj.img)
            #     print(obj.blocks)

            return None
            raise Exception(f'No matching object found in {img_name}!')

        else:
            return confirmed_matches

    else:
        missing_blocks = len(mentioned_blocks) - len(objects)
        print(f'{missing_blocks} blocks not detected in {img_name}.jpg!')  # TODO: handle exception
        return None
