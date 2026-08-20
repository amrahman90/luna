Global NAC DTMs

Shapefile of LROC Digital Terrain Models on the lunar surface and corresponding error analysis data. Polygons were generated from the DTM-derived products using GDAL and OGR tools. The shapefile uses the Moon_2000 geographic coordinate system and contains expanded error metrics compared to NAC DTM readmes.

Shapefile Field Descriptions:

dtm_name - PDS Sitename.
sitename - Sitename including context and comments.
dtm_vers - DTM version number.
images - List of image pairs used to produce the DTM.
resolution - DTM pixel scale (meters).
center_lon - Center longitude in degrees.
center_lat - Center latitude in degrees.
relat_le - Relative Linear Error. Vertical precision of the DTM, calculated at 90% confidence level by SOCET SET. Based on ground sampling distance, convergence angles, and image matching uncertainty (meters).
triang_rms - Triangulation RMS. Root mean square error of the multi-sensor triangulation performed by SOCET SET to align the images.
completion - Date that the DTM was completed.
num_profil - Number of LOLA profiles used to register the DTM.
lola_avg - Mean absolute error compared to LOLA tracks.
lola_rms - RMS absolute error compared to LOLA tracks.
adjust_rms - Adjusted RMS error of the additional global registration used for LOLA lat/lon/elv offset calculations. A high adjusted RMS may indicate that the lat., lon., and elv. offsets may be larger than reported. This registration does not affect the final DTM.
lat/lon/elv_offset - Offset from LOLA tracks in meters.
ln_jitter - Indicates the presence of jitter in the line direction.
sam_jitter - Indicates the presence of jitter in the sample direction.
isis_vers - ISIS version used for image processing.
cov_sqkm - Coverage of DTM (km2).
conv_angle - Convergence angle between the images in the stereo pair. 
num_stereo - Number of stereo pairs used to create DTM.
url - Link to the DTM on the LROC RDR website.
features - Key types of features found in the DTMs.

For more information, refer to: Henriksen, M. R., Manheim, M. R., Burns, K. N., Seymour, P., Speyerer, E. J., Deran, A., Boyd, A. K., Howington-Kraus, E., Rosiek, M. R., Archinal, B. A., and Robinson, M. S. (2017). Extracting accurate and precise topography from LROC narrow angle camera stereo observations. Icarus, 283, 122-137. https://doi.org/10.1016/j.icarus.2016.05.012

This shapefile contains the footprints of NAC DTMs released up through 2026-06-15.
