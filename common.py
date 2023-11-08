from dataclasses import dataclass
import struct
import re


@dataclass(frozen=True)
class Area:
    x: int
    y: int
    width: int
    height: int

    def __str__(self):
        return f"[{self.x}, {self.y}, {self.width}, {self.height}]"


@dataclass(frozen=True)
class RDParams:
    area: Area
    intra_mode: int
    isp_mode: int
    multi_ref_idx: int
    mip_flag: int
    lfnst_idx: int
    mts_flag: int


@dataclass(frozen=True)
class RDEntry:
    params: RDParams
    cost: float


LINE_PATTERN = re.compile(
    r"IntraCost T \[x=(\d+),y=(\d+),w=(\d+),h=(\d+)\] ([\d.]+) \((\d+),([\d-]+),(\d+),(\d+),(\d+),(\d+)\)"
)


def rd_entry(source):
    if (match := re.match(LINE_PATTERN, source)) is not None:
        [
            x,
            y,
            w,
            h,
            cost,
            intra_mode,
            isp_mode,
            multi_ref_idx,
            mip_flag,
            lfnst_idx,
            mts_flag,
        ] = match.groups()
        params = RDParams(
            Area(int(x), int(y), int(w), int(h)),
            int(intra_mode),
            int(isp_mode),
            int(multi_ref_idx),
            int(mip_flag),
            int(lfnst_idx),
            int(mts_flag),
        )
        return RDEntry(params, float(cost))
