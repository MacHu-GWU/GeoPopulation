===================================================================================================
Raw data
===================================================================================================
---------------------------------------------------------------------------------------------------
1. US Census 2010 data points:
	file = CenPop2010_Mean_BG.txt
	page link = https://www.census.gov/geo/reference/centersofpop.html
	file link = https://www.census.gov//geo/reference/docs/cenpop2010/blkgrp/CenPop2010_Mean_BG.txt
	
	description
		STATEFP:  2-character state FIPS code
		COUNTYFP:  3-character county FIPS code
		TRACTCE:  6-character census tract code
		BLKGRPCE:  1-character census block group code
		POPULATION:  2010 Census population tabulated for the block group
		LATITUDE:  latitude coordinate for the center of population for the block group
		LONGITUDE:  longitude coordinate for the center of population for the block group

	NOTICE:
		you can also find population by state, and population by city on this page
		
---------------------------------------------------------------------------------------------------
2. US county, state code:
	file = national_county.txt
	page link = https://www.census.gov/geo/reference/codes/cou.html
	file link = https://www.census.gov/geo/reference/docs/codes/national_county.txt
	
	description
		STATE	State Postal Code	FL
		STATEFP	State FIPS Code	12
		COUNTYFP	County FIPS Code	011
		COUNTYNAME	County Name and Legal/Statistical Area Description	Broward County
		CLASSFP	FIPS Class Code	H1

---------------------------------------------------------------------------------------------------
3. US states boundary polygon data1, fewer points:
	file = states.xml
	file link = http://econym.org.uk/gmap/states.xml

---------------------------------------------------------------------------------------------------
4. US states boundary polygon data2, more points:
	file = US Regions State Boundaries.csv
	page link = https://www.google.com/fusiontables/DataSource?docid=1-v6i33Lf_FjhRZcHKO0PG2DADipCg4L-dGiucAE
	
---------------------------------------------------------------------------------------------------
5. US land and marine coordinate data:
	file = NLDASmask_UMDunified.asc
	page link = http://ldas.gsfc.nasa.gov/nldas/NLDASspecs.php
	file link = http://ldas.gsfc.nasa.gov/nldas/asc/NLDASmask_UMDunified.asc
	
	description
		Column 1	Grid Column Number
		Column 2	Grid Row Number
		Column 3	Latitude (center of 1/8th-degree grid boxes)
		Column 4	Longitude (center of 1/8th-degree grid boxes)
		Column 5	Mask Value (0 = Water; 1 = Land)