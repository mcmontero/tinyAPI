# ----- Imports ---------------------------------------------------------------

import re

# ----- Public Classes --------------------------------------------------------

class CountryCode(object):
    '''
    Handles data and functionality for country codes.
    '''

    codes = {
        1: {
            "code": "93",
            "country_name": "Afghanistan"
        },

        2: {
            "code": "355",
            "country_name": "Albania"
        },

        3: {
            "code": "213",
            "country_name": "Algeria"
        },

        4: {
            "code": "1-684",
            "country_name": "American Samoa"
        },

        5: {
            "code": "376",
            "country_name": "Andorra"
        },

        6: {
            "code": "244",
            "country_name": "Angola"
        },

        7: {
            "code": "1-264",
            "country_name": "Anguilla"
        },

        8: {
            "code": "672",
            "country_name": "Antarctica"
        },

        9: {
            "code": "1-268",
            "country_name": "Antigua and Barbuda"
        },

        10: {
            "code": "54",
            "country_name": "Argentina"
        },

        11: {
            "code": "374",
            "country_name": "Armenia"
        },

        12: {
            "code": "297",
            "country_name": "Aruba"
        },

        13: {
            "code": "61",
            "country_name": "Australia"
        },

        14: {
            "code": "43",
            "country_name": "Austria"
        },

        15: {
            "code": "994",
            "country_name": "Azerbaijan"
        },

        16: {
            "code": "1-242",
            "country_name": "Bahamas"
        },

        17: {
            "code": "973",
            "country_name": "Bahrain"
        },

        18: {
            "code": "880",
            "country_name": "Bangladesh"
        },

        19: {
            "code": "1-246",
            "country_name": "Barbados"
        },

        20: {
            "code": "375",
            "country_name": "Belarus"
        },

        21: {
            "code": "32",
            "country_name": "Belgium"
        },

        22: {
            "code": "501",
            "country_name": "Belize"
        },

        23: {
            "code": "229",
            "country_name": "Benin"
        },

        24: {
            "code": "1-441",
            "country_name": "Bermuda"
        },

        25: {
            "code": "975",
            "country_name": "Bhutan"
        },

        26: {
            "code": "591",
            "country_name": "Bolivia"
        },

        27: {
            "code": "387",
            "country_name": "Bosnia and Herzegovina"
        },

        28: {
            "code": "267",
            "country_name": "Botswana"
        },

        29: {
            "code": "55",
            "country_name": "Brazil"
        },

        30: {
            "code": "246",
            "country_name": "British Indian Ocean Territory"
        },

        31: {
            "code": "1-284",
            "country_name": "British Virgin Islands"
        },

        32: {
            "code": "673",
            "country_name": "Brunei"
        },

        33: {
            "code": "359",
            "country_name": "Bulgaria"
        },

        34: {
            "code": "226",
            "country_name": "Burkina Faso"
        },

        35: {
            "code": "257",
            "country_name": "Burundi"
        },

        36: {
            "code": "855",
            "country_name": "Cambodia"
        },

        37: {
            "code": "237",
            "country_name": "Cameroon"
        },

        38: {
            "code": "1",
            "country_name": "Canada"
        },

        39: {
            "code": "238",
            "country_name": "Cape Verde"
        },

        40: {
            "code": "1-345",
            "country_name": "Cayman Islands"
        },

        41: {
            "code": "236",
            "country_name": "Central African Republic"
        },

        42: {
            "code": "235",
            "country_name": "Chad"
        },

        43: {
            "code": "56",
            "country_name": "Chile"
        },

        44: {
            "code": "86",
            "country_name": "China"
        },

        45: {
            "code": "61",
            "country_name": "Christmas Island"
        },

        46: {
            "code": "61",
            "country_name": "Cocos Islands"
        },

        47: {
            "code": "57",
            "country_name": "Colombia"
        },

        48: {
            "code": "269",
            "country_name": "Comoros"
        },

        49: {
            "code": "682",
            "country_name": "Cook Islands"
        },

        50: {
            "code": "506",
            "country_name": "Costa Rica"
        },

        51: {
            "code": "385",
            "country_name": "Croatia"
        },

        52: {
            "code": "53",
            "country_name": "Cuba"
        },

        53: {
            "code": "599",
            "country_name": "Curacao"
        },

        54: {
            "code": "357",
            "country_name": "Cyprus"
        },

        55: {
            "code": "420",
            "country_name": "Czech Republic"
        },

        56: {
            "code": "243",
            "country_name": "Democratic Republic of the Congo"
        },

        57: {
            "code": "45",
            "country_name": "Denmark"
        },

        58: {
            "code": "253",
            "country_name": "Djibouti"
        },

        59: {
            "code": "1-767",
            "country_name": "Dominica"
        },

        60: {
            "code": "1-809",
            "country_name": "Dominican Republic"
        },

        61: {
            "code": "1-829",
            "country_name": "Dominican Republic"
        },

        62: {
            "code": "1-849",
            "country_name": "Dominican Republic"
        },

        63: {
            "code": "670",
            "country_name": "East Timor"
        },

        64: {
            "code": "593",
            "country_name": "Ecuador"
        },

        65: {
            "code": "20",
            "country_name": "Egypt"
        },

        66: {
            "code": "503",
            "country_name": "El Salvador"
        },

        67: {
            "code": "240",
            "country_name": "Equatorial Guinea"
        },

        68: {
            "code": "291",
            "country_name": "Eritrea"
        },

        69: {
            "code": "372",
            "country_name": "Estonia"
        },

        70: {
            "code": "251",
            "country_name": "Ethiopia"
        },

        71: {
            "code": "500",
            "country_name": "Falkland Islands"
        },

        72: {
            "code": "298",
            "country_name": "Faroe Islands"
        },

        73: {
            "code": "679",
            "country_name": "Fiji"
        },

        74: {
            "code": "358",
            "country_name": "Finland"
        },

        75: {
            "code": "33",
            "country_name": "France"
        },

        76: {
            "code": "689",
            "country_name": "French Polynesia"
        },

        77: {
            "code": "241",
            "country_name": "Gabon"
        },

        78: {
            "code": "220",
            "country_name": "Gambia"
        },

        79: {
            "code": "995",
            "country_name": "Georgia"
        },

        80: {
            "code": "49",
            "country_name": "Germany"
        },

        81: {
            "code": "233",
            "country_name": "Ghana"
        },

        82: {
            "code": "350",
            "country_name": "Gibraltar"
        },

        83: {
            "code": "30",
            "country_name": "Greece"
        },

        84: {
            "code": "299",
            "country_name": "Greenland"
        },

        85: {
            "code": "1-473",
            "country_name": "Grenada"
        },

        86: {
            "code": "1-671",
            "country_name": "Guam"
        },

        87: {
            "code": "502",
            "country_name": "Guatemala"
        },

        88: {
            "code": "44-1481",
            "country_name": "Guernsey"
        },

        89: {
            "code": "224",
            "country_name": "Guinea"
        },

        90: {
            "code": "245",
            "country_name": "Guinea-Bissau"
        },

        91: {
            "code": "592",
            "country_name": "Guyana"
        },

        92: {
            "code": "509",
            "country_name": "Haiti"
        },

        93: {
            "code": "504",
            "country_name": "Honduras"
        },

        94: {
            "code": "852",
            "country_name": "Hong Kong"
        },

        95: {
            "code": "36",
            "country_name": "Hungary"
        },

        96: {
            "code": "354",
            "country_name": "Iceland"
        },

        97: {
            "code": "91",
            "country_name": "India"
        },

        98: {
            "code": "62",
            "country_name": "Indonesia"
        },

        99: {
            "code": "98",
            "country_name": "Iran"
        },

        101: {
            "code": "964",
            "country_name": "Iraq"
        },

        102: {
            "code": "353",
            "country_name": "Ireland"
        },

        103: {
            "code": "44-1624",
            "country_name": "Isle of Man"
        },

        104: {
            "code": "972",
            "country_name": "Israel"
        },

        105: {
            "code": "39",
            "country_name": "Italy"
        },

        106: {
            "code": "225",
            "country_name": "Ivory Coast"
        },

        107: {
            "code": "1-876",
            "country_name": "Jamaica"
        },

        108: {
            "code": "81",
            "country_name": "Japan"
        },

        109: {
            "code": "44-1534",
            "country_name": "Jersey"
        },

        110: {
            "code": "962",
            "country_name": "Jordan"
        },

        111: {
            "code": "7",
            "country_name": "Kazakhstan"
        },

        112: {
            "code": "254",
            "country_name": "Kenya"
        },

        113: {
            "code": "686",
            "country_name": "Kiribati"
        },

        114: {
            "code": "383",
            "country_name": "Kosovo"
        },

        115: {
            "code": "965",
            "country_name": "Kuwait"
        },

        116: {
            "code": "996",
            "country_name": "Kyrgyzstan"
        },

        117: {
            "code": "856",
            "country_name": "Laos"
        },

        118: {
            "code": "371",
            "country_name": "Latvia"
        },

        119: {
            "code": "961",
            "country_name": "Lebanon"
        },

        120: {
            "code": "266",
            "country_name": "Lesotho"
        },

        121: {
            "code": "231",
            "country_name": "Liberia"
        },

        122: {
            "code": "218",
            "country_name": "Libya"
        },

        123: {
            "code": "423",
            "country_name": "Liechtenstein"
        },

        124: {
            "code": "370",
            "country_name": "Lithuania"
        },

        125: {
            "code": "352",
            "country_name": "Luxembourg"
        },

        126: {
            "code": "853",
            "country_name": "Macao"
        },

        127: {
            "code": "389",
            "country_name": "Macedonia"
        },

        128: {
            "code": "261",
            "country_name": "Madagascar"
        },

        129: {
            "code": "265",
            "country_name": "Malawi"
        },

        130: {
            "code": "60",
            "country_name": "Malaysia"
        },

        131: {
            "code": "960",
            "country_name": "Maldives"
        },

        132: {
            "code": "223",
            "country_name": "Mali"
        },

        133: {
            "code": "356",
            "country_name": "Malta"
        },

        134: {
            "code": "692",
            "country_name": "Marshall Islands"
        },

        135: {
            "code": "222",
            "country_name": "Mauritania"
        },

        136: {
            "code": "230",
            "country_name": "Mauritius"
        },

        137: {
            "code": "262",
            "country_name": "Mayotte"
        },

        138: {
            "code": "52",
            "country_name": "Mexico"
        },

        139: {
            "code": "691",
            "country_name": "Micronesia"
        },

        140: {
            "code": "373",
            "country_name": "Moldova"
        },

        141: {
            "code": "377",
            "country_name": "Monaco"
        },

        142: {
            "code": "976",
            "country_name": "Mongolia"
        },

        143: {
            "code": "382",
            "country_name": "Montenegro"
        },

        144: {
            "code": "1-664",
            "country_name": "Montserrat"
        },

        145: {
            "code": "212",
            "country_name": "Morocco"
        },

        146: {
            "code": "258",
            "country_name": "Mozambique"
        },

        147: {
            "code": "95",
            "country_name": "Myanmar"
        },

        148: {
            "code": "264",
            "country_name": "Namibia"
        },

        149: {
            "code": "674",
            "country_name": "Nauru"
        },

        150: {
            "code": "977",
            "country_name": "Nepal"
        },

        151: {
            "code": "31",
            "country_name": "Netherlands"
        },

        152: {
            "code": "599",
            "country_name": "Netherlands Antilles"
        },

        153: {
            "code": "687",
            "country_name": "New Caledonia"
        },

        154: {
            "code": "64",
            "country_name": "New Zealand"
        },

        155: {
            "code": "505",
            "country_name": "Nicaragua"
        },

        156: {
            "code": "227",
            "country_name": "Niger"
        },

        157: {
            "code": "234",
            "country_name": "Nigeria"
        },

        158: {
            "code": "683",
            "country_name": "Niue"
        },

        159: {
            "code": "850",
            "country_name": "North Korea"
        },

        160: {
            "code": "1-670",
            "country_name": "Northern Mariana Islands"
        },

        161: {
            "code": "47",
            "country_name": "Norway"
        },

        162: {
            "code": "968",
            "country_name": "Oman"
        },

        163: {
            "code": "92",
            "country_name": "Pakistan"
        },

        164: {
            "code": "680",
            "country_name": "Palau"
        },

        165: {
            "code": "970",
            "country_name": "Palestine"
        },

        166: {
            "code": "507",
            "country_name": "Panama"
        },

        167: {
            "code": "675",
            "country_name": "Papua New Guinea"
        },

        168: {
            "code": "595",
            "country_name": "Paraguay"
        },

        169: {
            "code": "51",
            "country_name": "Peru"
        },

        170: {
            "code": "63",
            "country_name": "Philippines"
        },

        171: {
            "code": "64",
            "country_name": "Pitcairn"
        },

        172: {
            "code": "48",
            "country_name": "Poland"
        },

        173: {
            "code": "351",
            "country_name": "Portugal"
        },

        174: {
            "code": "1-787",
            "country_name": "Puerto Rico"
        },

        175: {
            "code": "1-939",
            "country_name": "Puerto Rico"
        },

        176: {
            "code": "974",
            "country_name": "Qatar"
        },

        177: {
            "code": "242",
            "country_name": "Republic of the Congo"
        },

        178: {
            "code": "262",
            "country_name": "Reunion"
        },

        179: {
            "code": "40",
            "country_name": "Romania"
        },

        180: {
            "code": "7",
            "country_name": "Russia"
        },

        181: {
            "code": "250",
            "country_name": "Rwanda"
        },

        182: {
            "code": "590",
            "country_name": "Saint Barthelemy"
        },

        183: {
            "code": "290",
            "country_name": "Saint Helena"
        },

        184: {
            "code": "1-869",
            "country_name": "Saint Kitts and Nevis"
        },

        185: {
            "code": "1-758",
            "country_name": "Saint Lucia"
        },

        186: {
            "code": "590",
            "country_name": "Saint Martin"
        },

        187: {
            "code": "508",
            "country_name": "Saint Pierre and Miquelon"
        },

        188: {
            "code": "1-784",
            "country_name": "Saint Vincent and the Grenadines"
        },

        189: {
            "code": "685",
            "country_name": "Samoa"
        },

        190: {
            "code": "378",
            "country_name": "San Marino"
        },

        191: {
            "code": "239",
            "country_name": "Sao Tome and Principe"
        },

        192: {
            "code": "966",
            "country_name": "Saudi Arabia"
        },

        193: {
            "code": "221",
            "country_name": "Senegal"
        },

        194: {
            "code": "381",
            "country_name": "Serbia"
        },

        195: {
            "code": "248",
            "country_name": "Seychelles"
        },

        196: {
            "code": "232",
            "country_name": "Sierra Leone"
        },

        197: {
            "code": "65",
            "country_name": "Singapore"
        },

        198: {
            "code": "1-721",
            "country_name": "Sint Maarten"
        },

        199: {
            "code": "421",
            "country_name": "Slovakia"
        },

        200: {
            "code": "386",
            "country_name": "Slovenia"
        },

        201: {
            "code": "677",
            "country_name": "Solomon Islands"
        },

        202: {
            "code": "252",
            "country_name": "Somalia"
        },

        203: {
            "code": "27",
            "country_name": "South Africa"
        },

        204: {
            "code": "82",
            "country_name": "South Korea"
        },

        205: {
            "code": "211",
            "country_name": "South Sudan"
        },

        206: {
            "code": "34",
            "country_name": "Spain"
        },

        207: {
            "code": "94",
            "country_name": "Sri Lanka"
        },

        208: {
            "code": "249",
            "country_name": "Sudan"
        },

        209: {
            "code": "597",
            "country_name": "Suriname"
        },

        210: {
            "code": "47",
            "country_name": "Svalbard and Jan Mayen"
        },

        211: {
            "code": "268",
            "country_name": "Swaziland"
        },

        212: {
            "code": "46",
            "country_name": "Sweden"
        },

        213: {
            "code": "41",
            "country_name": "Switzerland"
        },

        214: {
            "code": "963",
            "country_name": "Syria"
        },

        215: {
            "code": "886",
            "country_name": "Taiwan"
        },

        216: {
            "code": "992",
            "country_name": "Tajikistan"
        },

        217: {
            "code": "255",
            "country_name": "Tanzania"
        },

        218: {
            "code": "66",
            "country_name": "Thailand"
        },

        219: {
            "code": "228",
            "country_name": "Togo"
        },

        220: {
            "code": "690",
            "country_name": "Tokelau"
        },

        221: {
            "code": "676",
            "country_name": "Tonga"
        },

        222: {
            "code": "1-868",
            "country_name": "Trinidad and Tobago"
        },

        223: {
            "code": "216",
            "country_name": "Tunisia"
        },

        224: {
            "code": "90",
            "country_name": "Turkey"
        },

        225: {
            "code": "993",
            "country_name": "Turkmenistan"
        },

        226: {
            "code": "1-649",
            "country_name": "Turks and Caicos Islands"
        },

        227: {
            "code": "688",
            "country_name": "Tuvalu"
        },

        228: {
            "code": "1-340",
            "country_name": "U.S. Virgin Islands"
        },

        229: {
            "code": "256",
            "country_name": "Uganda"
        },

        230: {
            "code": "380",
            "country_name": "Ukraine"
        },

        231: {
            "code": "971",
            "country_name": "United Arab Emirates"
        },

        232: {
            "code": "44",
            "country_name": "United Kingdom"
        },

        233: {
            "code": "1",
            "country_name": "United States"
        },

        234: {
            "code": "598",
            "country_name": "Uruguay"
        },

        235: {
            "code": "998",
            "country_name": "Uzbekistan"
        },

        236: {
            "code": "678",
            "country_name": "Vanuatu"
        },

        237: {
            "code": "379",
            "country_name": "Vatican"
        },

        238: {
            "code": "58",
            "country_name": "Venezuela"
        },

        239: {
            "code": "84",
            "country_name": "Vietnam"
        },

        240: {
            "code": "681",
            "country_name": "Wallis and Futuna"
        },

        241: {
            "code": "212",
            "country_name": "Western Sahara"
        },

        242: {
            "code": "967",
            "country_name": "Yemen"
        },

        243: {
            "code": "260",
            "country_name": "Zambia"
        },

        244: {
            "code": "263",
            "country_name": "Zimbabwe"
        }
    }

    def get(self, id, stripped=True):
        self.__validate_id(id)

        return \
            (re.sub('[^0-9]', '', self.codes[id]['code'])
                if stripped is True else
             self.codes[id]['code'])


    def get_country_name(self, id):
        self.__validate_id(id)

        return self.codes[id]['country_name']


    def __validate_id(self, id):
        if id not in self.codes.keys():
            raise RuntimeError('no such country code ID "{}"'.format(id))
