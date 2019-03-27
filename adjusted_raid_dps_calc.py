# adjusted_raid_dps_calc.py
#
# Attempts to contribute raid DPS increase to self
# and removes external DPS contributions from self
# to determine true raid DPS comparison
import argparse
import copy
import json
import random
import sys
import itertools


class Job(object):
    def __init__(self, name, json_obj):
        self.name = name
        self.base_score = json_obj["score"]
        self.melee = json_obj["melee"] if "melee" in json_obj else False
        self.ranged = json_obj["ranged"] if "ranged" in json_obj else False
        self.physical_damage_percent = json_obj["physical"] if "physical" in json_obj else 0.0
        self.magical_damage_percent = json_obj["magical"] if "magical" in json_obj else 0.0
        self.damage_all = 0.0
        self.damage_physical = 0.0
        self.damage_magical = 0.0
        self.damage_single = 0.0
        self.score = self.base_score
        if "damage" in json_obj:
            damage_obj = json_obj["damage"]
            if "all" in damage_obj:
                self.damage_all = damage_obj["all"]
            if "physical" in damage_obj:
                self.damage_physical = damage_obj["physical"]
            if "magical" in damage_obj:
                self.damage_magical = damage_obj["magical"]
            if "single" in damage_obj:
                self.damage_single = damage_obj["single"]


class Output(object):
    def __init__(self, job_name, base_score):
        self.name = job_name
        self.base_score = base_score
        self.lowest_seen_score = 100.0
        self.highest_seen_score = 0.0
        self.average_score = 0.0
        self.result_count = 0.0
        self.highest_seen_score_group = ''

    def record_result(self, score, comp):
        if score < self.lowest_seen_score:
            self.lowest_seen_score = score
        if score > self.highest_seen_score:
            self.highest_seen_score = score
            self.highest_seen_score_group = ' '.join(comp)
        self.average_score = (score + (self.average_score * self.result_count)) / (self.result_count + 1)
        self.result_count += 1

    def print_results(self):
        print '{0}: base_score:{1} max_adjusted:{2} min_adjusted:{3} avg_adjusted:{4}'.format(
            self.name, self.base_score, self.highest_seen_score, self.lowest_seen_score, self.average_score)


def load_job_data():
    with open("jobs.json", "r") as read_file:
        return json.load(read_file)
    return None


def calc_group_score(comp):
    print "Running calc for group comp: {0} {1} {2}".format(comp[0].name, comp[1].name, comp[2].name)

    total_adjusted_score = 0.0
    # increase this jobs score by the bonuses from other group members
    for n in range(3):
        other_jobs = copy.deepcopy(comp)
        this_job = other_jobs.pop(n)

        for other_job in other_jobs:
            if other_job.damage_all != 0.0:
                this_job.score += (other_job.damage_all / 100.0) * this_job.base_score
            if other_job.damage_physical > 0.0 and this_job.physical_damage_percent > 0.0:
                # TODO: Mod by this_job physical_damage_percent
                this_job.score += (other_job.damage_physical / 100.0) * this_job.base_score
            if other_job.damage_magical > 0.0 and this_job.magical_damage_percent > 0.0:
                # TODO: Mod by this_job magical_damage_percent
                this_job.score += (other_job.damage_magical / 100.0) * this_job.base_score
        total_adjusted_score += this_job.score
    return total_adjusted_score


def comp_filter(comp):
    # do not allow all phys damage
    # do not allow all magical damage
    phys_count = 0
    mag_count = 0
    for job in comp:
        if job.name == 'RDM':
            continue
        if job.physical_damage_percent > 0.0:
            phys_count += 1
        if job.magical_damage_percent > 0.0:
            mag_count += 1

    return mag_count < 3 and phys_count < 3


def main():
    parser = argparse.ArgumentParser(prog="adjusted_raid_dps_calc", description='Calculate true raid DPS of FFXIV jobs',
                                     add_help=True)
    parser.add_argument('--fixed_job', type=str, help='Fix one of the jobs',
                        default='')

    args = parser.parse_args()

    job_data = load_job_data()
    if not job_data:
        raise RuntimeError('Unable to load job data.')

    # create all combinations of 3 DPSers ('ABCD', 2) => AA AB AC AD BB BC BD CC CD DD
    # we exclude the 4th DPS since that will always be reserved for a BRD/MCH and their calculations are too complex
    combinations = [list(x) for x in itertools.combinations_with_replacement(job_data.keys(), 3)]
    # convert to Job objs
    combinations = [[Job(y, job_data[y]) for y in x] for x in combinations]
    # certain comps are deemed "dumb", filter those out
    combinations = [x for x in combinations if comp_filter(x)]
    print "{0} group comp combinations generated".format(len(combinations))
    # combinations = [x for x in combinations if fixed_job in x]
    max_adjusted_score = 0.0
    max_comp = []
    for comp in combinations:
        total_adjusted_score = calc_group_score(comp)
        if total_adjusted_score > max_adjusted_score:
            max_adjusted_score = total_adjusted_score
            max_comp = comp
        print 'Base score: {0}'.format(sum([x.base_score for x in comp]))
        print 'Adjusted score: {0}'.format(total_adjusted_score)

    print 'Max comp: {0} adjusted score: {1}'.format(' '.join(x.name for x in max_comp), max_adjusted_score)


if __name__ == "__main__":
    if not main():
        sys.exit(1)
