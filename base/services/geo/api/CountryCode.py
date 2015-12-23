# ----- Imports ---------------------------------------------------------------

import re

# ----- Public Classes --------------------------------------------------------

class CountryCode(object):
    '''
    Handles data and functionality for country codes.
    '''

    codes = {
        213: {
            "code": "1",
            "country_name": "United States"
        },

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
            "code": "376",
            "country_name": "Andorra"
        },

        5: {
            "code": "244",
            "country_name": "Angola"
        },

        6: {
            "code": "672",
            "country_name": "Antarctica"
        },

        7: {
            "code": "54",
            "country_name": "Argentina"
        },

        8: {
            "code": "374",
            "country_name": "Armenia"
        },

        9: {
            "code": "297",
            "country_name": "Aruba"
        },

        10: {
            "code": "61",
            "country_name": "Australia"
        },

        11: {
            "code": "43",
            "country_name": "Austria"
        },

        12: {
            "code": "994",
            "country_name": "Azerbaijan"
        },

        13: {
            "code": "973",
            "country_name": "Bahrain"
        },

        14: {
            "code": "880",
            "country_name": "Bangladesh"
        },

        15: {
            "code": "375",
            "country_name": "Belarus"
        },

        16: {
            "code": "32",
            "country_name": "Belgium"
        },

        17: {
            "code": "501",
            "country_name": "Belize"
        },

        18: {
            "code": "229",
            "country_name": "Benin"
        },

        19: {
            "code": "975",
            "country_name": "Bhutan"
        },

        20: {
            "code": "591",
            "country_name": "Bolivia"
        },

        21: {
            "code": "387",
            "country_name": "Bosnia and Herzegovina"
        },

        22: {
            "code": "267",
            "country_name": "Botswana"
        },

        23: {
            "code": "55",
            "country_name": "Brazil"
        },

        24: {
            "code": "246",
            "country_name": "British Indian Ocean Territory"
        },

        25: {
            "code": "673",
            "country_name": "Brunei"
        },

        26: {
            "code": "359",
            "country_name": "Bulgaria"
        },

        27: {
            "code": "226",
            "country_name": "Burkina Faso"
        },

        28: {
            "code": "257",
            "country_name": "Burundi"
        },

        29: {
            "code": "855",
            "country_name": "Cambodia"
        },

        30: {
            "code": "237",
            "country_name": "Cameroon"
        },

        31: {
            "code": "1",
            "country_name": "Canada"
        },

        32: {
            "code": "238",
            "country_name": "Cape Verde"
        },

        33: {
            "code": "236",
            "country_name": "Central African Republic"
        },

        34: {
            "code": "235",
            "country_name": "Chad"
        },

        35: {
            "code": "56",
            "country_name": "Chile"
        },

        36: {
            "code": "86",
            "country_name": "China"
        },

        37: {
            "code": "61",
            "country_name": "Christmas Island"
        },

        38: {
            "code": "61",
            "country_name": "Cocos Islands"
        },

        39: {
            "code": "57",
            "country_name": "Colombia"
        },

        40: {
            "code": "269",
            "country_name": "Comoros"
        },

        41: {
            "code": "682",
            "country_name": "Cook Islands"
        },

        42: {
            "code": "506",
            "country_name": "Costa Rica"
        },

        43: {
            "code": "385",
            "country_name": "Croatia"
        },

        44: {
            "code": "53",
            "country_name": "Cuba"
        },

        45: {
            "code": "599",
            "country_name": "Curacao"
        },

        46: {
            "code": "357",
            "country_name": "Cyprus"
        },

        47: {
            "code": "420",
            "country_name": "Czech Republic"
        },

        48: {
            "code": "243",
            "country_name": "Democratic Republic of the Congo"
        },

        49: {
            "code": "45",
            "country_name": "Denmark"
        },

        50: {
            "code": "253",
            "country_name": "Djibouti"
        },

        51: {
            "code": "670",
            "country_name": "East Timor"
        },

        52: {
            "code": "593",
            "country_name": "Ecuador"
        },

        53: {
            "code": "20",
            "country_name": "Egypt"
        },

        54: {
            "code": "503",
            "country_name": "El Salvador"
        },

        55: {
            "code": "240",
            "country_name": "Equatorial Guinea"
        },

        56: {
            "code": "291",
            "country_name": "Eritrea"
        },

        57: {
            "code": "372",
            "country_name": "Estonia"
        },

        58: {
            "code": "251",
            "country_name": "Ethiopia"
        },

        59: {
            "code": "500",
            "country_name": "Falkland Islands"
        },

        60: {
            "code": "298",
            "country_name": "Faroe Islands"
        },

        61: {
            "code": "679",
            "country_name": "Fiji"
        },

        62: {
            "code": "358",
            "country_name": "Finland"
        },

        63: {
            "code": "33",
            "country_name": "France"
        },

        64: {
            "code": "689",
            "country_name": "French Polynesia"
        },

        65: {
            "code": "241",
            "country_name": "Gabon"
        },

        66: {
            "code": "220",
            "country_name": "Gambia"
        },

        67: {
            "code": "995",
            "country_name": "Georgia"
        },

        68: {
            "code": "49",
            "country_name": "Germany"
        },

        69: {
            "code": "233",
            "country_name": "Ghana"
        },

        70: {
            "code": "350",
            "country_name": "Gibraltar"
        },

        71: {
            "code": "30",
            "country_name": "Greece"
        },

        72: {
            "code": "299",
            "country_name": "Greenland"
        },

        73: {
            "code": "502",
            "country_name": "Guatemala"
        },

        74: {
            "code": "224",
            "country_name": "Guinea"
        },

        75: {
            "code": "245",
            "country_name": "Guinea-Bissau"
        },

        76: {
            "code": "592",
            "country_name": "Guyana"
        },

        77: {
            "code": "509",
            "country_name": "Haiti"
        },

        78: {
            "code": "504",
            "country_name": "Honduras"
        },

        79: {
            "code": "852",
            "country_name": "Hong Kong"
        },

        80: {
            "code": "36",
            "country_name": "Hungary"
        },

        81: {
            "code": "354",
            "country_name": "Iceland"
        },

        82: {
            "code": "91",
            "country_name": "India"
        },

        83: {
            "code": "62",
            "country_name": "Indonesia"
        },

        84: {
            "code": "98",
            "country_name": "Iran"
        },

        85: {
            "code": "964",
            "country_name": "Iraq"
        },

        86: {
            "code": "353",
            "country_name": "Ireland"
        },

        87: {
            "code": "972",
            "country_name": "Israel"
        },

        88: {
            "code": "39",
            "country_name": "Italy"
        },

        89: {
            "code": "225",
            "country_name": "Ivory Coast"
        },

        90: {
            "code": "81",
            "country_name": "Japan"
        },

        91: {
            "code": "962",
            "country_name": "Jordan"
        },

        92: {
            "code": "7",
            "country_name": "Kazakhstan"
        },

        93: {
            "code": "254",
            "country_name": "Kenya"
        },

        94: {
            "code": "686",
            "country_name": "Kiribati"
        },

        95: {
            "code": "383",
            "country_name": "Kosovo"
        },

        96: {
            "code": "965",
            "country_name": "Kuwait"
        },

        97: {
            "code": "996",
            "country_name": "Kyrgyzstan"
        },

        98: {
            "code": "856",
            "country_name": "Laos"
        },

        99: {
            "code": "371",
            "country_name": "Latvia"
        },

        100: {
            "code": "961",
            "country_name": "Lebanon"
        },

        101: {
            "code": "266",
            "country_name": "Lesotho"
        },

        102: {
            "code": "231",
            "country_name": "Liberia"
        },

        103: {
            "code": "218",
            "country_name": "Libya"
        },

        104: {
            "code": "423",
            "country_name": "Liechtenstein"
        },

        105: {
            "code": "370",
            "country_name": "Lithuania"
        },

        106: {
            "code": "352",
            "country_name": "Luxembourg"
        },

        107: {
            "code": "853",
            "country_name": "Macao"
        },

        108: {
            "code": "389",
            "country_name": "Macedonia"
        },

        109: {
            "code": "261",
            "country_name": "Madagascar"
        },

        110: {
            "code": "265",
            "country_name": "Malawi"
        },

        111: {
            "code": "60",
            "country_name": "Malaysia"
        },

        112: {
            "code": "960",
            "country_name": "Maldives"
        },

        113: {
            "code": "223",
            "country_name": "Mali"
        },

        114: {
            "code": "356",
            "country_name": "Malta"
        },

        115: {
            "code": "692",
            "country_name": "Marshall Islands"
        },

        116: {
            "code": "222",
            "country_name": "Mauritania"
        },

        117: {
            "code": "230",
            "country_name": "Mauritius"
        },

        118: {
            "code": "262",
            "country_name": "Mayotte"
        },

        119: {
            "code": "52",
            "country_name": "Mexico"
        },

        120: {
            "code": "691",
            "country_name": "Micronesia"
        },

        121: {
            "code": "373",
            "country_name": "Moldova"
        },

        122: {
            "code": "377",
            "country_name": "Monaco"
        },

        123: {
            "code": "976",
            "country_name": "Mongolia"
        },

        124: {
            "code": "382",
            "country_name": "Montenegro"
        },

        125: {
            "code": "212",
            "country_name": "Morocco"
        },

        126: {
            "code": "258",
            "country_name": "Mozambique"
        },

        127: {
            "code": "95",
            "country_name": "Myanmar"
        },

        128: {
            "code": "264",
            "country_name": "Namibia"
        },

        129: {
            "code": "674",
            "country_name": "Nauru"
        },

        130: {
            "code": "977",
            "country_name": "Nepal"
        },

        131: {
            "code": "31",
            "country_name": "Netherlands"
        },

        132: {
            "code": "599",
            "country_name": "Netherlands Antilles"
        },

        133: {
            "code": "687",
            "country_name": "New Caledonia"
        },

        134: {
            "code": "64",
            "country_name": "New Zealand"
        },

        135: {
            "code": "505",
            "country_name": "Nicaragua"
        },

        136: {
            "code": "227",
            "country_name": "Niger"
        },

        137: {
            "code": "234",
            "country_name": "Nigeria"
        },

        138: {
            "code": "683",
            "country_name": "Niue"
        },

        139: {
            "code": "850",
            "country_name": "North Korea"
        },

        141: {
            "code": "47",
            "country_name": "Norway"
        },

        142: {
            "code": "968",
            "country_name": "Oman"
        },

        143: {
            "code": "92",
            "country_name": "Pakistan"
        },

        144: {
            "code": "680",
            "country_name": "Palau"
        },

        145: {
            "code": "970",
            "country_name": "Palestine"
        },

        146: {
            "code": "507",
            "country_name": "Panama"
        },

        147: {
            "code": "675",
            "country_name": "Papua New Guinea"
        },

        148: {
            "code": "595",
            "country_name": "Paraguay"
        },

        149: {
            "code": "51",
            "country_name": "Peru"
        },

        150: {
            "code": "63",
            "country_name": "Philippines"
        },

        151: {
            "code": "64",
            "country_name": "Pitcairn"
        },

        152: {
            "code": "48",
            "country_name": "Poland"
        },

        153: {
            "code": "351",
            "country_name": "Portugal"
        },

        156: {
            "code": "974",
            "country_name": "Qatar"
        },

        157: {
            "code": "242",
            "country_name": "Republic of the Congo"
        },

        158: {
            "code": "262",
            "country_name": "Reunion"
        },

        159: {
            "code": "40",
            "country_name": "Romania"
        },

        160: {
            "code": "7",
            "country_name": "Russia"
        },

        161: {
            "code": "250",
            "country_name": "Rwanda"
        },

        162: {
            "code": "590",
            "country_name": "Saint Barthelemy"
        },

        163: {
            "code": "290",
            "country_name": "Saint Helena"
        },

        166: {
            "code": "590",
            "country_name": "Saint Martin"
        },

        167: {
            "code": "508",
            "country_name": "Saint Pierre and Miquelon"
        },

        169: {
            "code": "685",
            "country_name": "Samoa"
        },

        170: {
            "code": "378",
            "country_name": "San Marino"
        },

        171: {
            "code": "239",
            "country_name": "Sao Tome and Principe"
        },

        172: {
            "code": "966",
            "country_name": "Saudi Arabia"
        },

        173: {
            "code": "221",
            "country_name": "Senegal"
        },

        174: {
            "code": "381",
            "country_name": "Serbia"
        },

        175: {
            "code": "248",
            "country_name": "Seychelles"
        },

        176: {
            "code": "232",
            "country_name": "Sierra Leone"
        },

        177: {
            "code": "65",
            "country_name": "Singapore"
        },

        179: {
            "code": "421",
            "country_name": "Slovakia"
        },

        180: {
            "code": "386",
            "country_name": "Slovenia"
        },

        181: {
            "code": "677",
            "country_name": "Solomon Islands"
        },

        182: {
            "code": "252",
            "country_name": "Somalia"
        },

        183: {
            "code": "27",
            "country_name": "South Africa"
        },

        184: {
            "code": "82",
            "country_name": "South Korea"
        },

        185: {
            "code": "211",
            "country_name": "South Sudan"
        },

        186: {
            "code": "34",
            "country_name": "Spain"
        },

        187: {
            "code": "94",
            "country_name": "Sri Lanka"
        },

        188: {
            "code": "249",
            "country_name": "Sudan"
        },

        189: {
            "code": "597",
            "country_name": "Suriname"
        },

        190: {
            "code": "47",
            "country_name": "Svalbard and Jan Mayen"
        },

        191: {
            "code": "268",
            "country_name": "Swaziland"
        },

        192: {
            "code": "46",
            "country_name": "Sweden"
        },

        193: {
            "code": "41",
            "country_name": "Switzerland"
        },

        194: {
            "code": "963",
            "country_name": "Syria"
        },

        195: {
            "code": "886",
            "country_name": "Taiwan"
        },

        196: {
            "code": "992",
            "country_name": "Tajikistan"
        },

        197: {
            "code": "255",
            "country_name": "Tanzania"
        },

        198: {
            "code": "66",
            "country_name": "Thailand"
        },

        199: {
            "code": "228",
            "country_name": "Togo"
        },

        200: {
            "code": "690",
            "country_name": "Tokelau"
        },

        201: {
            "code": "676",
            "country_name": "Tonga"
        },

        203: {
            "code": "216",
            "country_name": "Tunisia"
        },

        204: {
            "code": "90",
            "country_name": "Turkey"
        },

        205: {
            "code": "993",
            "country_name": "Turkmenistan"
        },

        207: {
            "code": "688",
            "country_name": "Tuvalu"
        },

        209: {
            "code": "256",
            "country_name": "Uganda"
        },

        210: {
            "code": "380",
            "country_name": "Ukraine"
        },

        211: {
            "code": "971",
            "country_name": "United Arab Emirates"
        },

        212: {
            "code": "44",
            "country_name": "United Kingdom"
        },

        214: {
            "code": "598",
            "country_name": "Uruguay"
        },

        215: {
            "code": "998",
            "country_name": "Uzbekistan"
        },

        216: {
            "code": "678",
            "country_name": "Vanuatu"
        },

        217: {
            "code": "379",
            "country_name": "Vatican"
        },

        218: {
            "code": "58",
            "country_name": "Venezuela"
        },

        219: {
            "code": "84",
            "country_name": "Vietnam"
        },

        220: {
            "code": "681",
            "country_name": "Wallis and Futuna"
        },

        221: {
            "code": "212",
            "country_name": "Western Sahara"
        },

        222: {
            "code": "967",
            "country_name": "Yemen"
        },

        223: {
            "code": "260",
            "country_name": "Zambia"
        },

        224: {
            "code": "263",
            "country_name": "Zimbabwe"
        }
    }

    def get(self, id):
        self.__validate_id(id)

        return self.codes[id]['code']


    def get_country_name(self, id):
        self.__validate_id(id)

        return self.codes[id]['country_name']


    def __validate_id(self, id):
        if id not in self.codes.keys():
            raise RuntimeError('no such country code ID "{}"'.format(id))
