#!/usr/bin/env python

import enum
from dataclasses import dataclass
from collections import namedtuple
import yaml

Schedule = namedtuple("Schedule", "unit start stop")


@dataclass
class Clock:
    hour: int
    minute: int = 0


class Activation(enum.Enum):
    boolean = 1
    linear = 2
    sigmoid = 3


class Profile(enum.Enum):
    on = 1
    PWM = 2


@dataclass
class Device:
    power: int
    activation: Activation
    profile: Profile


class HeatCable:
    def __init__(self, power, temperature):
        self.dev = Device(
            power=power, activation=Activation.boolean, profile=Profile.on
        )
        self.temperature = temperature
        self.heat = self.temperature

    def tick(self):
        pass


class Stove:
    def __init__(self, power):
        self.dev = Device(
            power=power, activation=Activation.linear, profile=Profile.PWM
        )

    def tick(self):
        pass


class CoffeePot:
    def __init__(self, power):
        self.dev = Device(
            power=power, activation=Activation.boolean, profile=Profile.on
        )

    def tick(self):
        pass


class Charger:
    def __init__(self, power):
        self.dev = Device(
            power=power, activation=Activation.sigmoid, profile=Profile.on
        )

    def tick(self):
        pass


def _parse_time(config):
    return config.get("start"), config.get("end")


def _parse_entry(name, config):
    typ = config["config"]
    nam = typ["id"]
    power = typ.get("power")
    temp = typ.get("temperature")
    if nam == "HeatCable":
        return HeatCable(power=power, temperature=temp)
    elif nam == "Stove":
        return Stove(power=power)
    elif nam == "CoffeePot":
        return CoffeePot(power=power)
    elif nam == "Charger":
        return Charger(power=power)
    raise ValueError(f"Unknown type {nam}")


def parse_schedule(sch):
    for name, cfg in sch.items():
        yield {name: (_parse_entry(name, cfg), _parse_time(cfg))}


def main():
    from sys import argv

    if len(argv) != 2:
        exit("Usage: powgen schedule.yml")

    with open(argv[1]) as sch_file:
        schedule = list(parse_schedule(yaml.safe_load(sch_file)))
    print(schedule)


if __name__ == "__main__":
    main()
