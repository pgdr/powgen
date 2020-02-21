#!/usr/bin/env python

import enum
from dataclasses import dataclass
from collections import namedtuple

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


class Stove:
    def __init__(self, power):
        self.dev = Device(
            power=power, activation=Activation.linear, profile=Profile.PWM
        )


class CoffeePot(HeatCable):
    def __init__(self, power):
        self.heater = HeatCable(power, 80)


class Charger:
    def __init__(self, power):
        self.dev = Device(
            power=power, activation=Activation.sigmoid, profile=Profile.on
        )


def main():
    from sys import argv

    if len(argv) != 1:
        exit("Usage: powgen")

    schedule = {
        "bathroom": Schedule(HeatCable(1600, 30), None, None),
        "car": Schedule(Charger(5000), Clock(20), Clock(7, 45)),
        "stove": Schedule(Stove(4000), Clock(16), Clock(16, 30)),
        "coffee": Schedule(CoffeePot(400), Clock(7, 15), Clock(7, 30)),
    }


if __name__ == "__main__":
    main()
