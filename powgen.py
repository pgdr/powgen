#!/usr/bin/env python

import math
import random
import enum
from dataclasses import dataclass
from collections import namedtuple
import yaml
import noise


Schedule = namedtuple("Schedule", "name unit start end")


def perlin(time):
    return max(0.0, math.pi * 20 + 50 * noise.pnoise1(time * 0.005, 1))


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

    def _profile(self, p, on_time):
        if self.profile == Profile.on:
            return p
        if on_time % 19 == 17:
            return 0
        return p

    def compute(self, time):
        power = self.power
        if self.activation == Activation.linear:
            power = self.power / max(1, (4.5 - time))
        if self.activation == Activation.sigmoid:
            power = self.power * (1.0 / (1.0 + pow(math.e, -(time / 13.0))))
        return self._profile(power, time)


class HeatCable:
    def __init__(self, power, temperature):
        self.dev = Device(
            power=power, activation=Activation.boolean, profile=Profile.on
        )
        self.temperature = temperature
        self.heat = self.temperature
        self.on = False
        self.on_time = 0

    def tick(self):
        if self.on:
            if self.heat > self.temperature * 1.2:
                self.on = False
                self.on_time = 0
                return 0
            else:
                self.on_time += 1
                self.heat += (self.dev.power / 1000.0) * 0.7 * random.random()
                return self.dev.compute(time=self.on_time)
        else:
            self.heat -= 0.5 / 60 + math.log(max(0.1, self.heat)) / 20.0
            if self.heat < self.temperature * 0.8:
                self.on = True
                return self.dev.compute(time=self.on_time)
            else:
                return 0


class Stove:
    def __init__(self, power):
        self.dev = Device(
            power=power, activation=Activation.linear, profile=Profile.PWM
        )
        self.on = False
        self.on_time = 0

    def tick(self):
        if self.on:
            self.on_time += 1
            return self.dev.compute(time=self.on_time)
        else:
            self.on_time = 0
            return 0


class CoffeePot:
    def __init__(self, power):
        self.dev = Device(
            power=power, activation=Activation.boolean, profile=Profile.on
        )
        self.on = False
        self.on_time = 0

    def tick(self):
        if self.on:
            self.on_time += 1
            return self.dev.compute(time=self.on_time)
        else:
            self.on_time = 0
            return 0


class Charger:
    def __init__(self, power, capacity):
        self.dev = Device(
            power=power, activation=Activation.sigmoid, profile=Profile.on
        )
        self.capacity = capacity
        self.on = False
        self.on_time = 0

    def tick(self):
        if self.on:
            self.on_time += 1
            if self.on_time * self.dev.power / 60.0 > self.capacity:
                self.on = False
            return self.dev.compute(time=self.on_time)
        else:
            self.on_time = 0
            return 0


def _parse_time(t):
    if isinstance(t, int):
        return t, 0
    if not t:
        return None
    if ":" in t:
        return tuple(int(x) for x in t.split(":"))
    return int(t), 0


def _parse_entry(name, config):
    typ = config["config"]
    nam = typ["id"]
    power = typ.get("power")
    temp = typ.get("temperature")
    cap = typ.get("capacity")
    if nam == "HeatCable":
        return HeatCable(power=power, temperature=temp)
    elif nam == "Stove":
        return Stove(power=power)
    elif nam == "CoffeePot":
        return CoffeePot(power=power)
    elif nam == "Charger":
        return Charger(power=power, capacity=cap)
    raise ValueError(f"Unknown type {nam}")


def parse_schedule(sch):
    for name, cfg in sch.items():
        yield Schedule(
            name,
            _parse_entry(name, cfg),
            _parse_time(cfg.get("start")),
            _parse_time(cfg.get("end")),
        )


def _initialize(schedule):
    ns = []
    for elt in schedule:
        ns.append(elt)
    return ns


def _update(schedule, day, hour, minute):
    total = 0
    devs = set()
    for elt in schedule:
        if (
            elt.start is not None
            and (hour, minute) > elt.start
            and random.random() > 0.8
        ):
            elt.unit.on = True
        if elt.end is not None and (hour, minute) > elt.end and random.random() > 0.8:
            elt.unit.on = False

        if elt.unit.on:
            devs.add(elt.name)

        total += elt.unit.tick()
    return total, devs


def game(schedule, days=5):
    schedule = _initialize(schedule)

    all_devices = sorted(elt.name for elt in schedule)
    print(f"datetime,power,{','.join(all_devices)}")

    def dev_chi(devs):
        for d in all_devices:
            if d in devs:
                yield "1"
            else:
                yield "0"

    for day in range(days):
        # if day % 7 in (5, 6):   # weekend
        for hour in range(24):
            for minute in range(60):
                power, devs = _update(schedule, day, hour, minute)
                power += perlin(days * 24 * 60 + hour * 24 + minute)
                print(
                    f"2020-02-{17+day:02d} {hour:02d}:{minute:02d}:00.000000,{power:.1f},{','.join(dev_chi(devs))}"
                )


def main():
    from sys import argv

    if len(argv) != 2:
        exit("Usage: powgen schedule.yml")

    with open(argv[1]) as sch_file:
        schedule = list(parse_schedule(yaml.safe_load(sch_file)))

    game(schedule)


if __name__ == "__main__":
    main()
