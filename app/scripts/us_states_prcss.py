from openpyxl import load_workbook


def process_fips_codes(filepath):

  STATE_CODE = 1
  COUNTY_CODE = 2
  COUNTY_SUBDIVISION = 3
  PLACE_CODE = 4
  CONSOLIDATED_CITY = 5
  NAME = 6
  codes = {}
  wb = load_workbook(filepath, read_only=True)
  ws = wb.active

  for row in ws.iter_rows(min_row=6):

    state = row[STATE_CODE].value
    if not state == "00":
      if state not in codes:
        name = row[NAME].value
        codes[state] = {
            "name": name,
            "counties": {},
            "places": {},
            "consolidated_cities": {}
        }
        continue

      county = row[COUNTY_CODE].value
      if not county == "000":
        if county not in codes[state]["counties"]:
          name = row[NAME].value
          codes[state]["counties"][county] = {"name": name, "subdivisions": {}}
          continue

        county_subdiv = row[COUNTY_SUBDIVISION].value
        if not county_subdiv == "000000":
          name = row[NAME].value
          codes[state]["counties"][county]["subdivisions"][
              county_subdiv] = name
          continue

      place = row[PLACE_CODE].value
      if not place == "00000":
        name = row[NAME].value
        codes[state]["places"][place] = {"name": name}
        continue

      consolidated_city = row[CONSOLIDATED_CITY].value
      if not consolidated_city == "00000":
        name = row[NAME].value
        codes[state]["consolidated_cities"][consolidated_city] = {"name": name}
  return codes


def get_consolidated_cities(states):
  for state_code, state in states.items():
    for city_code, city in state["consolidated_cities"].items():
      print("city: {} located in state: {}".format(city, state["name"]))


def get_counties_of(state_name, states):
  for state_code, state in states.items():
    if state["name"] == state_name:
      for county_code, county in state["counties"].items():
        print("county: {} of {}".format(county["name"], state_name))

      print("number of counties: {}".format(len(state["counties"])))
      return
