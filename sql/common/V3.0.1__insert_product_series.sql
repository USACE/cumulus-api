-- insert all single-product product series

INSERT INTO product_series
        (id,
        slug,
        label,
        dss_fpart,
        parameter_id,
        description,
        unit_id,
        suite_id,
        dss_datatype_id,
        deleted)
SELECT      
    CASE
        WHEN slug = 'abrfc-qpe-01h' THEN '7a3aba12-b1dd-40dc-9c86-cddd5c4a98fb'::UUID
        WHEN slug = 'abrfc-qpf-06h' THEN '97461796-da75-4191-8dcb-83197382eb58'::UUID
        WHEN slug = 'aprfc-qpe-06h' THEN '62826e12-e15d-4726-a50e-85d6ad83b7cb'::UUID
        WHEN slug = 'aprfc-qpf-06h' THEN '45e11c81-afea-4f29-871c-0bbbceb30843'::UUID
        WHEN slug = 'aprfc-qte-01h' THEN 'bffbd434-5400-4db3-b3db-e284b66828df'::UUID
        WHEN slug = 'aprfc-qtf-01h' THEN 'a2087445-4c47-4b9f-ae47-0da2bdda5c11'::UUID
        WHEN slug = 'cbrfc-mpe' THEN 'c980d10a-7c5b-4459-8b22-1d2291c0ff3a'::UUID
        WHEN slug = 'cnrfc-nbm-qpf-06h' THEN '6badcd12-9597-4ab4-9898-d15b8598374b'::UUID
        WHEN slug = 'cnrfc-nbm-qtf-01h' THEN '259ee566-bacd-41e5-9d34-a1cf17a7c23c'::UUID
        WHEN slug = 'cnrfc-qpe-06h' THEN '128e63f9-7849-4a6c-ab7f-71d06c2cc168'::UUID
        WHEN slug = 'cnrfc-qpf-06h' THEN '3d404882-d76b-4734-85e3-5f8fd9f93367'::UUID
        WHEN slug = 'hrrr-total-precip' THEN 'f48086e0-6ed0-4118-9055-91f771fe0313'::UUID
        WHEN slug = 'lmrfc-qpe-01h' THEN 'd8517b89-5405-4c0d-815f-4ed776dcc4de'::UUID
        WHEN slug = 'lmrfc-qpf-06h' THEN '74c99af7-31c0-4644-8e7c-2d43fe6fd385'::UUID
        WHEN slug = 'marfc-fmat-06h' THEN 'f96cb262-01e9-4872-aa70-046845de0e15'::UUID
        WHEN slug = 'marfc-nbmt-01h' THEN 'f8a2c226-2dee-4c55-80bd-dc38fe4eee28'::UUID
        WHEN slug = 'marfc-rtmat-01h' THEN 'c9f15462-b4df-4f07-ab51-78ff64bec138'::UUID
        WHEN slug = 'mbrfc-krf-fct-airtemp-01h' THEN '21c92025-50eb-4f4d-a2bc-70554eb78d5a'::UUID
        WHEN slug = 'mbrfc-krf-qpe-01h' THEN '3b981bbf-8672-4fe9-a67c-e294f86b08f2'::UUID
        WHEN slug = 'mbrfc-krf-qpf-06h' THEN '30d575f0-d661-46b0-82c8-18f77d6c439c'::UUID
        WHEN slug = 'naefs-mean-qpf-06h' THEN 'adfe0322-adb0-4edd-9993-969aaae99d23'::UUID
        WHEN slug = 'naefs-mean-qtf-06h' THEN '34f4f6ee-4a62-4dd1-b323-2c73a4a6c20c'::UUID
        WHEN slug = 'nbm-co-airtemp' THEN '0b79b1d1-c885-47b2-8e8e-12f18d86c753'::UUID
        WHEN slug = 'nbm-co-qpf' THEN '15555b20-45c8-4b38-b206-65ae8b6304eb'::UUID
        WHEN slug = 'nbm-co-qpf-06h' THEN '2d63f685-e7d1-44ed-904b-3acb9c9bc2c9'::UUID
        WHEN slug = 'nbm-co-qtf-03h' THEN 'b1b19d6c-eaf2-4fa7-8f31-3e80a4b57e1d'::UUID
        WHEN slug = 'nbm-co-qtf-06h' THEN '0fdb2ccf-82e6-44a9-a64f-df2a274c0a83'::UUID
        WHEN slug = 'ncep-mrms-gaugecorr-qpe-01h' THEN '1eb98aa1-813c-43f9-82b2-a005bf893498'::UUID
        WHEN slug = 'ncep-mrms-v12-msqpe01h-p1-alaska' THEN '5cbf5a57-110e-47af-bfa6-5ea4fed20188'::UUID
        WHEN slug = 'ncep-mrms-v12-msqpe01h-p1-carib' THEN '84151e96-8365-4b2a-9e4f-8f0fdbdeafd1'::UUID
        WHEN slug = 'ncep-mrms-v12-msqpe01h-p2-alaska' THEN '2c007158-b8e9-49c2-8a95-c7a1b2cf8cbf'::UUID
        WHEN slug = 'ncep-mrms-v12-msqpe01h-p2-carib' THEN '8355e729-17a6-45b5-80f2-fc18910b40c8'::UUID
        WHEN slug = 'ncep-mrms-v12-multisensor-qpe-01h-pass1' THEN '260c2d3a-eb03-4c00-84c0-5f001af168c1'::UUID
        WHEN slug = 'ncep-mrms-v12-multisensor-qpe-01h-pass2' THEN '5059d09f-77d2-4ebb-84b5-5300f0919c68'::UUID
        WHEN slug = 'ncep-rtma-ru-anl-airtemp' THEN 'fe54e18b-bab0-4161-ae3d-09e7b13993b2'::UUID
        WHEN slug = 'ncep-stage4-mosaic-01h' THEN '367ea1d5-5885-4330-9ff4-8f9252b1680a'::UUID
        WHEN slug = 'ncep-stage4-mosaic-06h' THEN '7829c1ec-5dfd-4133-bbad-c47f503f3cb4'::UUID
        WHEN slug = 'ncep-stage4-mosaic-24h' THEN 'd30c9a8a-79c3-4c7d-b160-61a7c8daedd1'::UUID
        WHEN slug = 'ncrfc-mpe-01h' THEN 'ad4e65b6-aedf-4834-b832-4c0143145176'::UUID
        WHEN slug = 'ncrfc-rtmat-01h' THEN 'f35bb729-1a32-41d9-9ba6-d9eb07d537e4'::UUID
        WHEN slug = 'ndfd-conus-qpf-06h' THEN '5fabd4d8-a41b-4e01-b557-460c88e96681'::UUID
        WHEN slug = 'ndgd-leia98-precip' THEN 'd475cf3a-9cb6-4810-84a6-e5cd6bfe24c9'::UUID
        WHEN slug = 'ndgd-ltia98-airtemp' THEN '30e6aba7-8b6f-4c55-b1f3-49997e52acb9'::UUID
        WHEN slug = 'nerfc-qpe-01h' THEN 'c99507bf-0844-4f6d-9232-e272736dfc49'::UUID
        WHEN slug = 'nohrsc-snodas-coldcontent' THEN 'd144b70e-d70e-4565-85d8-1e3756e537c9'::UUID
        WHEN slug = 'nohrsc-snodas-coldcontent-interpolated' THEN '38078952-d509-42e6-a9cb-92aaa91d3e8d'::UUID
        WHEN slug = 'nohrsc-snodas-snowdepth' THEN '0eabca70-94ea-45e7-9795-ebb7daafc519'::UUID
        WHEN slug = 'nohrsc-snodas-snowdepth-interpolated' THEN '4863dbb2-863b-483d-ac39-9cf69f61aa60'::UUID
        WHEN slug = 'nohrsc-snodas-snowmelt' THEN '5b1f99b7-6116-49f7-aa4e-ac3ffcb25445'::UUID
        WHEN slug = 'nohrsc-snodas-snowmelt-interpolated' THEN '90f13640-6da1-4f50-bb71-306904364c85'::UUID
        WHEN slug = 'nohrsc-snodas-snowpack-average-temperature' THEN 'c69cd006-85f1-462c-9ed4-cd92d503afd3'::UUID
        WHEN slug = 'nohrsc-snodas-snowpack-average-temperature-interpolated' THEN 'e591b6ba-c0a6-4db7-8613-461b8a77ffb6'::UUID
        WHEN slug = 'nohrsc-snodas-swe' THEN 'c68f92e7-3d55-4700-9248-ee3c385fa6c8'::UUID
        WHEN slug = 'nohrsc-snodas-swe-corrections' THEN '54d97c29-3329-4193-9fa1-e1cf4b6c3cd7'::UUID
        WHEN slug = 'nohrsc-snodas-swe-interpolated' THEN 'c8bbc7e1-d676-449c-a240-8ca0f7ab18e3'::UUID
        WHEN slug = 'nsidc-ua-snowdepth-v1' THEN '2abae10a-8ef7-4463-9d72-dfca77d26717'::UUID
        WHEN slug = 'nsidc-ua-swe-v1' THEN '271c86a8-b362-495b-83a1-be62be92b256'::UUID
        WHEN slug = 'nwrfc-qpe-06h' THEN 'f1326551-07d5-4b84-b378-70eb23950814'::UUID
        WHEN slug = 'nwrfc-qpf-06h' THEN '255e0dd8-4bf2-4f46-ac0a-f201531802ea'::UUID
        WHEN slug = 'nwrfc-qte-06h' THEN '57209a70-acd1-4c53-9112-326a13221a3e'::UUID
        WHEN slug = 'nwrfc-qtf-06h' THEN '694a9db4-8fe3-44e5-8fdd-7c8bc690dd48'::UUID
        WHEN slug = 'prism-ppt-early' THEN '4fe2bd81-9b65-4bca-b2ef-ba657cb100a0'::UUID
        WHEN slug = 'prism-ppt-stable' THEN '82211641-3f70-4af3-a234-29a7a3bab69a'::UUID
        WHEN slug = 'prism-tmax-early' THEN '9dbcb15c-6bcb-47dd-ade4-97322da497ee'::UUID
        WHEN slug = 'prism-tmax-stable' THEN '4178f244-5378-4346-bcc6-516de36e13b2'::UUID
        WHEN slug = 'prism-tmin-early' THEN 'c8aa0457-eb88-4b6e-b9e8-47a9ee1cbda5'::UUID
        WHEN slug = 'prism-tmin-stable' THEN '15f468c7-5af1-4232-a61c-34478fdc6198'::UUID
        WHEN slug = 'serfc-qpe-01h' THEN '5c12d798-b1d2-4947-989a-1b40e89691dc'::UUID
        WHEN slug = 'serfc-qpf-06h' THEN 'a9a0dc6e-3ed3-41ad-8072-d0416a11edbd'::UUID
        WHEN slug = 'wpc-qpf-2p5km' THEN '4be0c80c-7a89-4381-985e-1d7fd3d569c4'::UUID
        WHEN slug = 'wrf-bc-dewpntt' THEN '63c0882a-c78d-4f80-8c82-0ed3de28b34f'::UUID
        WHEN slug = 'wrf-bc-groundt' THEN 'febbd2fe-0990-4f68-a886-29ed31213b66'::UUID
        WHEN slug = 'wrf-bc-lwdown' THEN 'e6dae8a5-1563-4176-9f97-543eaa8b840b'::UUID
        WHEN slug = 'wrf-bc-precipah' THEN 'd097e18c-48f9-486b-96f0-d8562f08ff67'::UUID
        WHEN slug = 'wrf-bc-pstarcrs' THEN '6c7946d4-6e1f-4fd7-ad75-737c0f4a1669'::UUID
        WHEN slug = 'wrf-bc-rh' THEN '85f2e557-e65b-45b0-8454-3e63528b1002'::UUID
        WHEN slug = 'wrf-bc-swdown' THEN 'da1b9490-ddce-4b9e-975a-e0c806e19d1c'::UUID
        WHEN slug = 'wrf-bc-t2' THEN 'f77a3113-0faa-4da6-bd2f-b38e3c238252'::UUID
        WHEN slug = 'wrf-bc-u10' THEN '4f8fefb9-cb2f-4630-8755-f6b1b6ef5a21'::UUID
        WHEN slug = 'wrf-bc-v10' THEN '27195859-de62-41b6-bf6b-61d8c5d5f118'::UUID
        WHEN slug = 'wrf-bc-vaporps' THEN '91be6837-73c5-484f-84fa-ef46e4f521f6'::UUID
        WHEN slug = 'wrf-columbia-airtemp' THEN '70257392-9d5c-4426-a98e-e53a20e03588'::UUID
        WHEN slug = 'wrf-columbia-dewpntt' THEN 'b1c77e7f-9e89-4236-958a-d95ac1dbcf8f'::UUID
        WHEN slug = 'wrf-columbia-groundt' THEN 'e9421319-6ca0-4a69-8bca-5a9ea9dc8407'::UUID
        WHEN slug = 'wrf-columbia-lwdown' THEN 'bfab0f5b-3adb-445e-89bc-81ce7f9202f2'::UUID
        WHEN slug = 'wrf-columbia-precip' THEN '834e6d4d-289f-4160-a33c-edde8c5a8df3'::UUID
        WHEN slug = 'wrf-columbia-precipah' THEN '50937a9d-2f19-4292-9dd5-b24594edb08b'::UUID
        WHEN slug = 'wrf-columbia-pstarcrs' THEN '8f585276-3a3d-4745-80a6-dfa6778a7e68'::UUID
        WHEN slug = 'wrf-columbia-rh' THEN '4e196585-3055-44ec-8777-26ee801f5e23'::UUID
        WHEN slug = 'wrf-columbia-swdown' THEN '96291450-63f4-4a7b-9ddb-6e5a58c7f66d'::UUID
        WHEN slug = 'wrf-columbia-t2' THEN 'b4796107-dda0-412a-ad6e-02f915497196'::UUID
        WHEN slug = 'wrf-columbia-u10' THEN '6241acf5-7ceb-486d-a2f6-95af74613a6c'::UUID
        WHEN slug = 'wrf-columbia-v10' THEN 'cb958d10-c375-45cc-a0d1-695cbba539d6'::UUID
        WHEN slug = 'wrf-columbia-vaporps' THEN '112084d4-d48a-4148-9e54-e982c37f6b38'::UUID
        ELSE '99999999-9999-9999-9999-999999999999'::UUID
        END AS id,
        slug,
        label,
        dss_fpart,
        parameter_id,
        description,
        unit_id,
        suite_id,
        dss_datatype_id,
        deleted
FROM    product
WHERE   slug NOT LIKE 'ndfd-conus-airtemp-%';


-- insert NDFD airtemp product series (referenced by three products)

INSERT INTO product_series
            (id,
             slug,
             label,
             dss_fpart,
             parameter_id,
             description,
             unit_id,
             suite_id,
             dss_datatype_id,
             deleted)
SELECT      'be844c72-703b-414c-bd41-cb0dbbdeabf5'::UUID AS id,
             'ndfd-conus-airtemp' AS slug,
             '' AS label,
             dss_fpart,
             parameter_id,
             'National Digital Forecast Database - Forecast Airtemp' AS description,
             unit_id,
             suite_id,
             dss_datatype_id,
             false
FROM        product
WHERE       slug = 'ndfd-conus-airtemp-01h';