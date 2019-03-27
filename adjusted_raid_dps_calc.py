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


def run(fixed_job):
    if fixed_job != "":
        print "Running calc for {0} job".format(fixed_job)
    else:
        print "Running calc for all jobs"

    job_data = load_job_data()
    if not job_data:
        raise RuntimeError('Unable to load job data.')
    job_keys = job_data.keys()

    # init our outputs
    outputs = {}
    for job_name in job_keys:
        outputs[job_name] = Output(job_name, job_data[job_name]["score"])

    # Create all combinations of 4 DPSers ('ABCD', 2) => AA AB AC AD BB BC BD CC CD DD
    combinations = [list(x) for x in itertools.combinations_with_replacement(job_keys, 4)]
    if fixed_job != "":
        # filter further by ensuring each combination includes at least 1 of fixed_job
        combinations = [x for x in combinations if fixed_job in x]

    print "{0} group comp combinations generated".format(len(combinations))

    # testing
    # combinations = [['NIN', 'SAM', 'DRG', 'SMN']]

    for comp in combinations:
        source_jobs = []
        for n in range(4):
            job_name = comp[n]
            job = Job(job_name, job_data[job_name])
            source_jobs.append(job)

        for n in range(4):
            jobs = copy.deepcopy(source_jobs)
            this_job = jobs.pop(n)

            # remove external score increases from other jobs in comp
            for other_job in jobs:
                if other_job.damage_all != 0.0:
                    this_job.score -= (other_job.damage_all / 100.0) * this_job.base_score
                if this_job.physical_damage_percent > 0.0 and other_job.damage_physical != 0.0:
                    # TODO: Mod by this_job physical_damage_percent
                    this_job.score -= (other_job.damage_physical / 100.0) * this_job.base_score
                if this_job.magical_damage_percent > 0.0 and other_job.damage_magical != 0.0:
                    # TODO: Mod by this_job magical_damage_percent
                    this_job.score -= (other_job.damage_magical / 100.0) * this_job.base_score

            # increase this jobs score by increases it gives others
            if this_job.damage_all != 0.0:
                for other_job in jobs:
                    this_job.score += (this_job.damage_all / 100.0) * other_job.base_score
            if this_job.damage_physical > 0.0:
                # TODO: Mod by this_job physical_damage_percent
                for other_job in jobs:
                    if other_job.physical_damage_percent > 0.0:
                        this_job.score += (this_job.damage_physical / 100.0) * other_job.base_score
            if this_job.damage_magical > 0.0:
                # TODO: Mod by this_job magical_damage_percent
                for other_job in jobs:
                    if other_job.magical_damage_percent > 0.0:
                        this_job.score += (this_job.damage_magical / 100.0) * other_job.base_score

            outputs[this_job.name].record_result(this_job.score, comp)

    print "Results:"
    for k, v in outputs.iteritems():
        v.print_results()


def main():
    parser = argparse.ArgumentParser(prog="adjusted_raid_dps_calc", description='Calculate true raid DPS of FFXIV jobs',
                                     add_help=True)
    parser.add_argument('--fixed_job', type=str, help='Fix one of the jobs',
                        default='')

    args = parser.parse_args()
    run(args.fixed_job)


if __name__ == "__main__":
    if not main():
        sys.exit(1)
