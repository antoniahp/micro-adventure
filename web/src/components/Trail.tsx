import type { Sky } from "../sky";

// A bird: two wings that flap (SMIL animation, which works in every browser).
const WINGS_UP = "M-8 2Q-4 -6 0 0Q4 -6 8 2";
const WINGS_DOWN = "M-8 -2Q-4 3 0 1Q4 3 8 -2";

function Bird({ y, scale, duration, delay, flap }: { y: number; scale: number; duration: number; delay: number; flap: boolean }) {
  return (
    <g className="bird" style={{ animationDuration: `${duration}s`, animationDelay: `${delay}s` }}>
      <g transform={`translate(0 ${y}) scale(${scale})`}>
        <path d={WINGS_UP} fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" opacity="0.9">
          {flap && <animate attributeName="d" dur="0.7s" repeatCount="indefinite" values={`${WINGS_UP};${WINGS_DOWN};${WINGS_UP}`} begin={`${delay % 0.7}s`} />}
        </path>
      </g>
    </g>
  );
}

const STARS = [
  [30, 36], [205, 22], [360, 30], [78, 74], [128, 28], [250, 50], [330, 80], [392, 62], [58, 20], [175, 66],
];
const FIREFLIES = [
  [60, 190], [120, 176], [230, 196], [330, 190], [372, 180],
];

// Scene for the start screen: a winding trail with things to find along the way.
// The sky, sun, moon, stars and lamp follow the hour (see sky.ts); birds fly by day, fireflies glow at night.
export default function Trail({ sky }: { sky: Sky }) {
  const reduceMotion = typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
  const day = 1 - sky.night;

  return (
    <svg className="trail" viewBox="0 0 400 230" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
      {/* stars */}
      <g fill="#fff" opacity={sky.night * 0.85}>
        {STARS.map(([x, y], i) => (
          <circle key={i} className="star" cx={x} cy={y} r={i % 3 === 0 ? 1.8 : 1.3} style={{ animationDelay: `${(i % 5) * 0.6}s` }} />
        ))}
      </g>

      {/* sun and moon */}
      {sky.sun && (
        <g>
          <circle className="sun-glow" cx={sky.sun.x} cy={sky.sun.y} r="34" fill={sky.sun.color} opacity="0.25" />
          <circle cx={sky.sun.x} cy={sky.sun.y} r="22" fill={sky.sun.color} />
        </g>
      )}
      {sky.moon && (
        <g transform={`translate(${sky.moon.x} ${sky.moon.y})`}>
          <circle r="26" fill="#F4F1FF" opacity="0.14" />
          <path d="M-3 -16A16 16 0 1 0 12 10A12 12 0 1 1 -3 -16z" fill="#F4F1FF" />
        </g>
      )}

      {/* clouds drifting by day */}
      <g opacity={day * 0.85} fill="#fff">
        <g className="cloud" style={{ animationDuration: "70s" }}>
          <ellipse cx="0" cy="72" rx="22" ry="7" />
          <ellipse cx="10" cy="66" rx="12" ry="8" />
        </g>
        <g className="cloud" style={{ animationDuration: "95s", animationDelay: "-40s" }}>
          <ellipse cx="0" cy="98" rx="18" ry="6" />
          <ellipse cx="-8" cy="93" rx="10" ry="7" />
        </g>
      </g>

      {/* birds: only while there is light */}
      {day > 0.4 && (
        <g>
          <Bird y={78} scale={1} duration={19} delay={-3} flap={!reduceMotion} />
          <Bird y={90} scale={0.75} duration={24} delay={-11} flap={!reduceMotion} />
          <Bird y={102} scale={0.6} duration={28} delay={-18} flap={!reduceMotion} />
        </g>
      )}

      {/* land */}
      <path d="M0 134C70 106 140 114 210 130S340 122 400 110V230H0z" fill="#6C54E0" />
      <path d="M0 152C80 142 160 148 230 152S350 150 400 142V230H0z" fill="#10A878" />

      {/* the trail */}
      <path d="M146 230C184 206 118 190 168 170S214 152 206 148L224 148C236 154 196 170 226 186S304 212 288 230z" fill="#F3EEFF" />

      {/* trees */}
      <g>
        <rect x="95" y="152" width="5" height="14" fill="#6b4a3a" />
        <circle cx="97.500" cy="143" r="14" fill="#0b7a58" />
        <circle cx="93" cy="139" r="6" fill="#14a06e" />
        <rect x="337" y="170" width="8" height="26" fill="#6b4a3a" />
        <circle cx="341" cy="156" r="25" fill="#0b7a58" />
        <circle cx="333" cy="150" r="10" fill="#14a06e" />
        <rect x="257" y="146" width="3" height="8" fill="#6b4a3a" />
        <circle cx="258.500" cy="142" r="8" fill="#0b7a58" />
      </g>

      {/* lamp post: glows more as the light fades */}
      <rect x="290" y="142" width="3" height="32" fill="#1b1a4a" />
      <circle cx="291.500" cy="139" r="22" fill="#FFB300" opacity={0.08 + sky.lamp * 0.3} />
      <circle cx="291.500" cy="139" r="13" fill="#FFB300" opacity={0.12 + sky.lamp * 0.28} />
      <circle cx="291.500" cy="139" r="5.500" fill={sky.lamp > 0.3 ? "#FFD25E" : "#FFB300"} />

      {/* signpost pointing along the trail */}
      <rect x="150" y="196" width="3" height="24" fill="#6b4a3a" />
      <path d="M144 190h24l6 5-6 5h-24z" fill="#FFB300" />

      {/* bench */}
      <rect x="100" y="187" width="38" height="4" rx="1" fill="#c98a4b" />
      <rect x="100" y="195" width="38" height="5" rx="1" fill="#c98a4b" />
      <rect x="103" y="200" width="3" height="8" fill="#1b1a4a" />
      <rect x="132" y="200" width="3" height="8" fill="#1b1a4a" />

      {/* obstacles on the trail: a rock and a puddle */}
      <ellipse cx="197" cy="187" rx="11" ry="7" fill="#8b86b8" />
      <ellipse cx="194" cy="184" rx="5" ry="3" fill="#a9a5d2" />
      <ellipse cx="252" cy="208" rx="19" ry="5" fill="#2E8BEA" />
      <ellipse className="puddle-shine" cx="248" cy="207" rx="7" ry="1.600" fill="#8cc4f7" />

      {/* flowers */}
      <g>
        <circle cx="40" cy="206" r="3.500" fill="#F25C54" />
        <circle cx="58" cy="216" r="3" fill="#FFB300" />
        <circle cx="28" cy="220" r="3" fill="#ff8fc7" />
        <circle cx="366" cy="216" r="3.500" fill="#F25C54" />
        <circle cx="384" cy="204" r="3" fill="#FFB300" />
        <circle cx="318" cy="222" r="3" fill="#ff8fc7" />
      </g>

      {/* fireflies at night */}
      <g fill="#FFE98A" opacity={sky.night}>
        {FIREFLIES.map(([x, y], i) => (
          <circle key={i} className="firefly" cx={x} cy={y} r="2" style={{ animationDelay: `${i * 0.7}s` }} />
        ))}
      </g>

      {/* foreground */}
      <path d="M0 216C40 208 84 214 112 230H0z" fill="#1b1a4a" />
      <path d="M400 208C370 206 342 216 314 230H400z" fill="#1b1a4a" />

      {/* the whole scene gets darker at night */}
      <rect width="400" height="230" fill="#0B1030" opacity={sky.night * 0.38} />
    </svg>
  );
}
