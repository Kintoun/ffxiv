# raid_comp_score_calc.py
#
# Attempts to calculate group composition score. Uses data from jobs.json
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
        self.tank = json_obj["tank"] if "tank" in json_obj else False
        self.healer = json_obj["healer"] if "healer" in json_obj else False
        self.melee = json_obj["melee"] if "melee" in json_obj else False
        self.ranged = json_obj["ranged"] if "ranged" in json_obj else False
        self.physical_damage_percent = json_obj["physical"] if "physical" in json_obj else 0.0
        self.magical_damage_percent = json_obj["magical"] if "magical" in json_obj else 0.0
        self.slashing_debuff = json_obj["debuff"] == "slashing" if "debuff" in json_obj else False
        self.piercing_debuff = json_obj["debuff"] == "piercing" if "debuff" in json_obj else False
        self.blunt_debuff = json_obj["debuff"] == "blunt" if "debuff" in json_obj else False
        self.main_stat = json_obj["main_stat"] if "main_stat" in json_obj else ""
        self.damage_type = json_obj["type"] if "type" in json_obj else ""
        self.damage_buff_all = 0.0
        self.damage_buff_physical = 0.0
        self.damage_buff_magical = 0.0
        self.damage_buff_single = 0.0
        self.score = self.base_score
        if "damage_buff" in json_obj:
            damage_buff_obj = json_obj["damage_buff"]
            if "all" in damage_buff_obj:
                self.damage_buff_all = damage_buff_obj["all"]
            if "physical" in damage_buff_obj:
                self.damage_buff_physical = damage_buff_obj["physical"]
            if "magical" in damage_buff_obj:
                self.damage_buff_magical = damage_buff_obj["magical"]
            if "single" in damage_buff_obj:
                self.damage_buff_single = damage_buff_obj["single"]


class CompOutput(object):
    def __init__(self, jobs, base_score, adjusted_score):
        self.jobs = jobs
        self.name = ' '.join(x.name for x in jobs)
        self.base_score = base_score
        self.adjusted_score = adjusted_score

    def print_results(self):
        print '{0}: adjusted:{1:.2f} base:{2:.2f}'.format(self.name, self.adjusted_score, self.base_score)


def load_job_data():
    with open("jobs.json", "r") as read_file:
        return json.load(read_file)
    return None


def calc_group_score(dps_jobs, non_dps_jobs):
    # print "Running calc for group comp: {0} {1} {2}".format(dps_jobs[0].name, dps_jobs[1].name, dps_jobs[2].name)

    total_base_score = 0.0
    total_adjusted_score = 0.0
    full_group = copy.deepcopy(dps_jobs) + copy.deepcopy(non_dps_jobs)
    # WAR tank always provides this and is a locked spot in the group
    has_slashing_debuff = True
    has_piercing_debuff = len(list(filter(lambda job: job.piercing_debuff, dps_jobs))) > 0
    has_blunt_debuff = len(list(filter(lambda job: job.blunt_debuff, dps_jobs))) > 0
    has_str_buff = len(list(filter(lambda job: job.main_stat == "STR", dps_jobs))) > 0
    has_dex_buff = len(list(filter(lambda job: job.main_stat == "DEX", dps_jobs))) > 0
    has_int_buff = len(list(filter(lambda job: job.main_stat == "INT", dps_jobs))) > 0
    # for each member in the group
    for n in range(len(full_group)):
        this_job = full_group[n]

        # increase this jobs score by the bonuses from other group members (includes self, bit hacky)
        for other_job in full_group:
            if other_job.damage_buff_all != 0.0:
                this_job.score += (other_job.damage_buff_all / 100.0) * this_job.base_score
            if other_job.damage_buff_physical > 0.0 and this_job.physical_damage_percent > 0.0:
                this_job.score += ((other_job.damage_buff_physical / 100.0) * this_job.base_score) * (this_job.physical_damage_percent / 100.0)
            if other_job.damage_buff_magical > 0.0 and this_job.magical_damage_percent > 0.0:
                this_job.score += ((other_job.damage_buff_magical / 100.0) * this_job.base_score) * (this_job.magical_damage_percent / 100.0)

        # this seems weird, but if we have any single target score increases just apply it to ourselves for simplicity
        if this_job.damage_buff_single:
            this_job.score += (this_job.damage_buff_single / 100.0) * this_job.base_score

        # increase score if debuff exists
        if has_slashing_debuff and this_job.damage_type == "slashing":
            this_job.score += 0.10 * this_job.base_score * (this_job.physical_damage_percent / 100.0)
        elif has_piercing_debuff and this_job.damage_type == "piercing":
            this_job.score += 0.05 * this_job.base_score * (this_job.physical_damage_percent / 100.0)
        elif has_blunt_debuff and this_job.damage_type == "blunt":
            this_job.score += 0.10 * this_job.base_score * (this_job.physical_damage_percent / 100.0)

        # apply party main stat bonus
        if has_str_buff and this_job.main_stat == "STR" or this_job.main_stat == "VIT":
            this_job.score += 0.03 * this_job.base_score
        elif has_dex_buff and this_job.main_stat == "DEX":
            this_job.score += 0.03 * this_job.base_score
        elif has_int_buff and this_job.main_stat == "INT":
            this_job.score += 0.03 * this_job.base_score

        total_base_score += this_job.base_score
        total_adjusted_score += this_job.score
    return total_base_score, total_adjusted_score


def is_dps_job(job_name):
    return job_name != 'PLD' and job_name != 'WAR' and job_name != 'SCH' and job_name != 'AST'


def comp_filter(comp):
    # do not allow all phys damage
    # do not allow all magical damage
    # RDM doesn't apply
    phys_count = len(list(filter(lambda job: job.name != 'RDM' and job.physical_damage_percent > 0.0, comp)))
    mag_count = len(list(filter(lambda job: job.name != 'RDM' and job.magical_damage_percent > 0.0, comp)))
    return mag_count < 3 and phys_count < 3


def main():
    parser = argparse.ArgumentParser(prog="raid_comp_score_calc",
                                     description='Calculate highest raid comp score for FFXIV', add_help=True)
    parser.add_argument('--fixed_comp', type=str, help='CSV list of jobs to use',
                        default='')
    parser.add_argument('--filter', type=int, help='Turn job filter on/off. Filters out all phys or all magic comps',
                        default='1')

    args = parser.parse_args()

    job_data = load_job_data()
    if not job_data:
        raise RuntimeError('Unable to load job data.')

    # Gather the DPS jobs only
    dps_job_keys = [x for x in job_data.keys() if is_dps_job(x)]

    if args.fixed_comp == '':
        # create all combinations of 3 DPSers ('ABCD', 2) => AA AB AC AD BB BC BD CC CD DD
        # we exclude the 4th DPS since that will always be reserved for a BRD/MCH and their calculations are too complex
        combinations = [list(x) for x in itertools.combinations_with_replacement(dps_job_keys, 3)]
        print "{0} group comp combinations generated".format(len(combinations))
    else:
        combinations = [args.fixed_comp.split(',')]
    # convert to Job objs
    combinations = [[Job(y, job_data[y]) for y in x] for x in combinations]
    if args.filter == 1:
        # certain comps are deemed "dumb", filter those out
        combinations = [x for x in combinations if comp_filter(x)]

    non_dps_jobs = [Job(x, job_data[x]) for x in job_data.keys() if not is_dps_job(x)]

    output = []
    for comp in combinations:
        total_base_score, total_adjusted_score = calc_group_score(comp, non_dps_jobs)
        output.append(CompOutput(comp, total_base_score, total_adjusted_score))

    output.sort(key=lambda i: i.adjusted_score)
    for o in output:
        o.print_results()


if __name__ == "__main__":
    if not main():
        sys.exit(1)
