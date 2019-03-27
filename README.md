# ffxiv
Assorted FFXIV tools

## raid_comp_score_calc

Attempts to calculate group composition score. Uses data manually sourced from fflogs for Omega: Alphascape (Savage). [Link](https://www.fflogs.com/zone/statistics/25/#dataset=95&class=Any)
2 weeks of data, set to top 5% parses
and a community sourced data sheet that shows "Raid DPS Gain" stats per job. [Link](https://docs.google.com/spreadsheets/d/1aSzKYCsE4_DUdDcxbxrRR272JECmETw3Hoq644ZWUZM/edit#gid=1564032043)

Score and DPS are equivalent on fflogs. Score is just DPS normalized across 0-100. If my group buffs yield a
"Raid DPS Gain" of 1% and the PLD's score is 50 then I modify the PLD's score by 1% resulting in 50.5. Adjusted group
comp score is achieved by applying this across all group members.

###### Assumptions:
- Tanks, Healers, and the 4th DPS's (always a BRD) buffs are left out since their buffs are constant.
- BRD's are also very hard to calculate "Raid DPS Gain" since Foe Requiem is mana based and toggled
- MCH is left out because LOOOL reroll BRD
- Certain buffs only apply to 'others' (MNK Brotherhood) but actually include self for simplicity
- Single target buffs are always on and don't check for a valid target (e.g. DRG Dragon Sight)
- Decent chance that SAM/BLM numbers are higher than other jobs since AST's generally throw the single target
cards their way
