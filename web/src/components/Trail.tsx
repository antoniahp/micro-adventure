// Scene for the start screen: a winding trail at dusk, with things to find along the way.
export default function Trail() {
  return (
    <svg className="trail" viewBox="0 0 400 230" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
      {/* sky: sun, birds, stars */}
      <circle cx="298" cy="116" r="40" fill="#FFB300" />
      <g fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" opacity="0.85">
        <path d="M250 62q7-7 14 0q7-7 14 0" />
        <path d="M300 40q5-5 10 0q5-5 10 0" />
      </g>
      <g fill="#fff" opacity="0.7">
        <circle cx="30" cy="36" r="1.6" />
        <circle cx="205" cy="22" r="1.4" />
        <circle cx="360" cy="30" r="1.6" />
      </g>

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

      {/* lamp post */}
      <rect x="290" y="142" width="3" height="32" fill="#1b1a4a" />
      <circle cx="291.500" cy="139" r="13" fill="#FFB300" opacity="0.28" />
      <circle cx="291.500" cy="139" r="5.500" fill="#FFB300" />

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
      <ellipse cx="248" cy="207" rx="7" ry="1.600" fill="#8cc4f7" />

      {/* flowers */}
      <g>
        <circle cx="40" cy="206" r="3.500" fill="#F25C54" />
        <circle cx="58" cy="216" r="3" fill="#FFB300" />
        <circle cx="28" cy="220" r="3" fill="#ff8fc7" />
        <circle cx="366" cy="216" r="3.500" fill="#F25C54" />
        <circle cx="384" cy="204" r="3" fill="#FFB300" />
        <circle cx="318" cy="222" r="3" fill="#ff8fc7" />
      </g>

      {/* foreground */}
      <path d="M0 216C40 208 84 214 112 230H0z" fill="#1b1a4a" />
      <path d="M400 208C370 206 342 216 314 230H400z" fill="#1b1a4a" />
    </svg>
  );
}
