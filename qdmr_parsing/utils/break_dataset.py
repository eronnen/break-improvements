
class NoiseDataException(RuntimeError):
    pass


# Data that is known to be misleading
DATA_BLACKLIST = [
    # a lot of 'and one' where 'one' should be '#1' in the training data
    'CLEVR_train_13650',
    'CLEVR_train_6425',
    'CLEVR_train_13127',
    'COMQA_train_cluster-1740-1',
    'COMQA_train_cluster-2081-1',
    'COMQA_train_cluster-2081-2',
    'DROP_train_history_2583_522fbbf6-3fe5-4b86-a8a6-16425d4cea56',
    'DROP_train_nfl_3241_9c8e6054-2d5b-40b1-974d-24ffbed073ca',
    'GEO_train_1',  # state with the largest - ??
    'DROP_train_nfl_1836_80da76d7-c5c4-434f-b140-fa1a7eb44107',  # second-largest?? why that -??
    'DROP_train_nfl_3433_3d010ebe-fd24-4ee1-bd0a-dee5f76f6c7a',
    'DROP_train_nfl_381_eb9bbe95-1169-421f-8e73-6845573a3dc0',
]

# Data that it's operations in the csv is wrong. we keep it in the training data but ignore the operations that written.
WRONG_TRAINING_OPERATION_LIST = [
    'CLEVR_train_1450',
    'CLEVR_train_16932',
    'CLEVR_train_2182',
    'CLEVR_train_6379',
    'GEO_train_126',
    'CWQ_train_WebQTest-380_4c7907860e095c22b6bac71653f566ab',
    'CWQ_train_WebQTrn-1022_a0de7a84fd8601231a8d987cd65e0e29',
    'CWQ_train_WebQTrn-142_9a43288a2ba3603595ca8acd460b05ae',

    # a lot of the 'flight number of' aggregate instead of project
    'ATIS_train_1092',
    'ATIS_train_1688',
    'ATIS_train_1751',
    'ATIS_train_1899',
    'ATIS_train_2837',
    'ATIS_train_3831',
    'ATIS_train_889',
    'ATIS_train_2837',
    'ATIS_train_3831',
    'ATIS_train_3831',
    'CWQ_train_WebQTrn-1592_f8bfbee9fa618c2a1d180919b690953b',
    'CWQ_train_WebQTrn-3222_6a11413726183556d331fe26f3cc1904',
    'DROP_train_history_1312_33bd9772-2083-4dab-bd8b-adff46bb2fd4',
    'DROP_train_history_217_bbf959b4-1956-4c40-a988-75f012f69187',
    'DROP_train_history_1836_d101816b-1b61-4300-bbba-a8197124f1a5',
    'DROP_train_history_1925_a38434a6-3335-4698-80de-425799d78426',
    'DROP_train_history_2540_343c45bc-64a5-479c-bc13-060347df8e8a',
    'DROP_train_nfl_2853_c6e4a829-9656-4227-865b-d7fb06616b1c',

    # a lot of 'deparment number of' aggregate instead of project
    'SPIDER_train_1253',
    'SPIDER_train_1328',
    'SPIDER_train_1329',
    'SPIDER_train_1463',
    'SPIDER_train_1601',
    'SPIDER_train_1602',
    'SPIDER_train_1611',
    'SPIDER_train_1612',
    'SPIDER_train_3117',
    'SPIDER_train_313',
    'SPIDER_train_327',
    'SPIDER_train_3417',
    'SPIDER_train_3419',
    'SPIDER_train_3433',
    'SPIDER_train_3445',
    'SPIDER_train_3505',
    'SPIDER_train_3509',
    'SPIDER_train_3906',
    'SPIDER_train_3907',
    'SPIDER_train_397',
    'SPIDER_train_398',
    'SPIDER_train_4081',
    'SPIDER_train_4082',
    'SPIDER_train_4083',
    'SPIDER_train_4087',
    'SPIDER_train_4091',
    'SPIDER_train_4723',
    'SPIDER_train_4724',
    'SPIDER_train_4944',
    'SPIDER_train_4976',
    'SPIDER_train_5042',
    'SPIDER_train_5099',
    'SPIDER_train_5114',
    'SPIDER_train_5115',
    'SPIDER_train_5448',
    'SPIDER_train_575',
    'SPIDER_train_576',
    'SPIDER_train_5780',
    'SPIDER_train_5781',
    'SPIDER_train_588',
    'SPIDER_train_597',
    'SPIDER_train_598',
    'SPIDER_train_6103',
    'SPIDER_train_6104',
    'SPIDER_train_6325',
    'SPIDER_train_6367',
    'SPIDER_train_6662',
    'SPIDER_train_6664',
    'SPIDER_train_6665',
    'SPIDER_train_6913',
    'SPIDER_train_802',
    'SPIDER_train_85',
    'SPIDER_train_86',

    # a lot of wrong 'project' instead of 'arithmetic' here
    'DROP_train_history_1089_4696b303-920b-4973-860e-1a9fad6045e8',
    'DROP_train_history_1312_c562dfb1-0dd2-4b0e-b09b-0fa344dde8d3',
    'DROP_train_history_1377_3480a931-fe65-4867-849d-9ec919501aff',
    'DROP_train_history_1428_2548d408-ee79-4fca-8bf9-f7663993e095',
    'DROP_train_history_1468_fc040aae-13e8-48a0-910b-09f65b00efcc',
    'DROP_train_history_1507_1ba7d0a5-82fb-4789-90e5-55020d2119d1',
    'DROP_train_history_162_4680d448-2273-457c-a598-7a12c3bc8c06',
    'DROP_train_history_167_19f96e39-823c-485b-bb88-66a54ee13394',
    'DROP_train_history_1675_e446f30a-36a7-42d1-95cb-67caae833e73',
    'DROP_train_history_1715_89ce7cd5-9fa5-4bb5-9f0f-f4c79064927d',
    'DROP_train_history_1726_2d9f7c8d-31d6-4609-872f-0a3a275a37c2',
    'DROP_train_history_1726_6aeca350-08ba-422a-a382-9d639b94b286',
    'DROP_train_history_1730_7093cf81-ffc3-48ed-8650-7ff27d66801c',
    'DROP_train_history_1732_059f3342-2ebd-4971-9648-7ff0d3607abe',
    'DROP_train_history_1735_ff52afe5-b66c-4e72-81cf-7d90bba16c2b',
    'DROP_train_history_1747_d5fe655c-feee-45d5-8f3c-af2a7e3738a1',
    'DROP_train_history_1751_87780cb0-5aeb-439b-9e89-ededbf30061f',
    'DROP_train_history_1751_f03c4226-c635-4613-981f-3f1cd33432f8',
    'DROP_train_history_1774_c791cb87-c0f8-452b-a70f-120e267c5fa3',
    'DROP_train_history_1776_da4f9eae-3232-4c51-9e7c-d30f1a3a54c7',
    'DROP_train_history_1776_db4c74c6-3332-45c8-86dd-87adfcfd76a7',
    'DROP_train_history_1784_6eed081a-1e7c-415f-99ac-8b8c8aebb71e',
    'DROP_train_history_1794_be614a0e-d375-40c6-9ad1-31a39c1b8e89',
    'DROP_train_history_1805_2c0773ff-b5ff-48ba-947c-3005ea307822',
    'DROP_train_history_1805_fc0f47e3-84bf-4e66-bb97-a9c66b9dc3ab',
    'DROP_train_history_1805_fc0f47e3-84bf-4e66-bb97-a9c66b9dc3ab',
    'DROP_train_history_1809_77c8d7bc-5ce6-4e04-ad46-84fa33e245d7',
    'DROP_train_history_1809_8f0461a7-a376-4e01-9a5c-b3d969acf4a9',
    'DROP_train_history_1818_0d9aac01-b625-45da-a05f-27eb1329e943',
    'DROP_train_history_1830_8f85ba76-c8a5-42ed-8eff-a2cb3da94687',
    'DROP_train_history_1830_b7e00f3d-67ad-4175-ad2b-4af4200c0a2b',
    'DROP_train_history_1830_d618afbf-9365-4df3-9146-b47bc076dc2c',
    'DROP_train_history_1834_44b9fbea-4948-42e3-84bf-ec5d9de1a8e3',
    'DROP_train_history_1845_7fc80f06-16aa-4878-bcc8-7e1eddad0bcf',
    'DROP_train_history_1845_8e8c2665-2e00-4159-b2ac-c933c7656db1',
    'DROP_train_history_1847_2f3f116f-5401-4c98-98fc-6338c92c8ea7',
    'DROP_train_history_1847_6de3b691-bafd-40af-af25-e5df64d5c477',
    'DROP_train_history_1847_71163c1c-0f02-45e9-92d2-96213d38be36',
    'DROP_train_history_1847_a7fb0ade-715c-456a-9ebe-0b7e3294996c',
    'DROP_train_history_1848_9816ce32-4bcc-4de8-8920-d55c6da4d0bc',
    'DROP_train_history_1849_3bc54012-0aa2-4e91-8664-3051e07b4966',
    'DROP_train_history_1849_4c649734-4402-481a-a677-c7bc7f31c888',
    'DROP_train_history_1857_0d591569-2f93-4003-a8b6-389fd54bf5f3',
    'DROP_train_history_1861_3bbcd121-a7f9-4f03-a1a7-75de60a8f1af',
    'DROP_train_history_1865_4c952be2-a1c3-4cf4-a5a6-5c070082bb62',
    'DROP_train_history_1866_441a09fc-bec7-4887-badd-c0f2172691e3',
    'DROP_train_history_1866_482d2497-69ee-4ac6-ab34-c2c161872313',
    'DROP_train_history_1866_be4943e7-8a3c-4d3f-a80c-f04168653fbd',
    'DROP_train_history_1867_294a2312-8923-49e0-a042-cfabd00b9296',
    'DROP_train_history_1870_276c678f-0cc5-4ce8-8ea6-f3349ab8ff42',
    'DROP_train_history_1872_5eca58c1-25a8-4115-ab44-561a162fc27a',
    'DROP_train_history_1873_8bcc2f89-d3c5-4eb0-92c7-4ab88f2ff907',
    'DROP_train_history_1873_f8692996-bed0-4470-a2a7-0abe23409ea1',
    'DROP_train_history_1877_1ed3dd00-6dd3-417a-8c3b-4cb090ce4233',
    'DROP_train_history_1877_aa30af8a-6e16-4729-bb03-9109854a67f5',
    'DROP_train_history_1882_c21db5a8-3fce-4eaa-8cac-337ae67e782c',
    'DROP_train_history_1889_94544726-3fe7-4e35-9647-01b1548e7df8',
    'DROP_train_history_1897_5a4bffc7-7a53-45c0-992c-6fac1a511277',
    'DROP_train_history_190_c77bfa16-7fb0-4be3-95e2-e382a06dbd65',
    'DROP_train_history_1911_f3f702c7-c76e-485f-94e2-2d431e92bb05',
    'DROP_train_history_1913_a4771bb0-aec6-47de-bda8-83eba64d8e75',
    'DROP_train_history_1915_a90d22cb-28d1-4dc3-873e-fcaabf514ca0',
    'DROP_train_history_1915_d9d2aa76-e062-4309-8136-272e05b198a6',
    'DROP_train_history_1918_08f98930-96d3-4509-bfb7-fc625f861ef6',
    'DROP_train_history_1920_23094333-f10a-45f6-99fe-abc8a2f19368',
    'DROP_train_history_1920_72b779d0-b673-4158-8321-7f971de80792',
    'DROP_train_history_1936_81011ddf-dcc6-47b3-aed6-8499263727c8',
    'DROP_train_history_1937_065a23fb-8cd3-474d-88c2-56ca600dac2e',
    'DROP_train_history_1941_eba7aadf-e57b-49bc-8f24-08dda3439687',
    'DROP_train_history_1955_709fec58-a1db-427e-a5d4-37fcd2d19503',
    'DROP_train_history_1957_b1d97578-86ca-490c-8324-61012e6be16c',
    'DROP_train_history_1966_f8804249-83d6-4c6a-8d0b-bf93d3995bc8',
    'DROP_train_history_1996_d55e1958-9fff-4d01-bb39-ea58cbfb61ee',
    'DROP_train_history_2013_04ac88fa-96cd-4c2e-90b0-a4516b8d013d',
    'DROP_train_history_2013_ad2597f0-d4c0-4dbf-8b38-39a1832e3a72',
    'DROP_train_history_2013_c7343399-484e-4c08-bb6c-c6e9c3cc933f',
    'DROP_train_history_2013_f0a4b3bc-5c90-41af-8507-a2de65eba4b7',
    'DROP_train_history_2056_4e5daa6a-6b67-4e54-a9eb-52fa18d5c73a',
    'DROP_train_history_2061_3721ca8e-d3c3-47e1-88da-0bacb713ca7d',
    'DROP_train_history_2061_769d53f5-2b62-4b0b-9bb7-dbbfcdbeb476',
    'DROP_train_history_2061_de2380bf-b7e7-4914-84cc-ec4ea64ad091',
    'DROP_train_history_2077_0533450b-9223-49e2-b73a-02977e87ad48',
    'DROP_train_history_2077_6ae86691-f180-4f14-96fe-bec609eacef7',
    'DROP_train_history_2077_8e2809b9-5f53-4cbc-abdd-06411dfd2209',
    'DROP_train_history_2093_703fa1de-7582-442b-8e0c-16838fa7e4ea',
    'DROP_train_history_2095_0720896c-ba79-4013-ad57-939d7d8030c1',
    'DROP_train_history_2104_b3e705f3-62db-48c5-b2ec-a7d167fd047d',
    'DROP_train_history_2128_007fb686-2521-46ae-83d2-0107e6c19a4a',
    'DROP_train_history_2141_65774080-005b-4faa-8d18-f65224b42f3d',
    'DROP_train_history_2141_be7d74bc-e6ca-4c5a-8db2-a83728863d8c',
    'DROP_train_history_2148_11dae5d7-db97-4a02-ac04-a38819afc0e7',
    'DROP_train_history_2148_3b3b3b2d-3ffb-4c23-9b50-67c3eda00869',
    'DROP_train_history_2149_97eb3d9d-a879-41da-9743-46996eb128c4',
    'DROP_train_history_2150_1db209af-11a5-4299-8c8a-a3bbfbe0cec0',
    'DROP_train_history_2150_9c3fa3fb-1067-4676-bfd5-e1b64a92b4f6',
    'DROP_train_history_2156_2980b49f-be79-4ea1-a047-f38dc5f3150e',
    'DROP_train_history_2156_725c6834-01fd-48e4-aab1-136e627199d3',
    'DROP_train_history_2156_dad90bf2-a9bb-4785-b5c8-4415f7cfc6c5',
    'DROP_train_history_2157_2796c624-9a18-4380-a605-b0ec25aea661',
    'DROP_train_history_2171_ed62e44f-2e05-4ebf-a870-6b524d18d64c',
    'DROP_train_history_2174_384c5f8f-3839-497f-a287-2333d6bdca38',
    'DROP_train_history_2182_63a59805-dd07-4f41-9603-6ca787411a07',
    'DROP_train_history_2206_e46a59d8-dddb-4faf-a101-710d2e21dab0',
    'DROP_train_history_2207_98f3a8b3-0b4e-4674-aa50-eb990769db01',
    'DROP_train_history_2222_9d223970-e8be-432d-8dd4-92adaa20e4fd',
    'DROP_train_history_2267_be6748b1-85f1-4c51-80f8-eef2bc61dbe1',
    'DROP_train_history_2274_bd38bf99-bbcf-4fb1-9672-8c7c873f2fc3',
    'DROP_train_history_2274_e14a9726-c9c1-4b45-b8b9-45b4234f0ab5',
    'DROP_train_history_2275_d842dcec-cf1f-40b5-a620-6b5c8ce8e61c',
    'DROP_train_history_2293_9e274357-17d2-4979-8715-7f0ce4aa8f41',
    'DROP_train_history_2300_03632533-d347-4b94-a3f5-a9b94f7907de',
    'DROP_train_history_2354_91089472-d816-4be4-baf4-9b2912fce6e5',
    'DROP_train_history_2358_3630303c-2abc-4f75-a10b-f1a8ce544573',
    'DROP_train_history_2365_e85e2c79-6599-47f7-ab63-014f1021ce34',
    'DROP_train_history_2366_2e6e35f3-90a5-4386-bb64-1f956a3172f9',
    'DROP_train_history_2366_9a91388f-de00-45b7-8e6c-be41391ccb2a',
    'DROP_train_history_2366_e62d2b63-203c-4066-a09c-741d9160bc92',
    'DROP_train_history_2373_78d53b3e-865f-4f13-b2a0-ea7b7bffaeab',
    'DROP_train_history_2407_38c9664e-910b-4ad0-8dbb-110cc30b2af0',
    'DROP_train_history_2413_8d56813f-ef22-4559-87b4-8e09786015e2',
    'DROP_train_history_2413_f034df89-d0af-4cc6-b078-da091fafd227',
    'DROP_train_history_2414_2148a198-a5ab-4fe1-b5a5-5efb3fd464c2',
    'DROP_train_history_2420_2bc848b0-fd9e-4129-8c3e-4eed43929ed0',
    'DROP_train_history_2420_490d6aea-15ea-4b03-9f7d-66feec857c6e',
    'DROP_train_history_2420_b27dc4c5-8916-4eda-a5a8-f088e3d246c7',
    'DROP_train_history_2420_b31a7e2d-32f9-4e43-ad13-ca2a7f5e8897',
    'DROP_train_history_2422_ebe331c9-970e-4208-93d7-a3b32f951553',
    'DROP_train_history_2449_aa527fbe-8374-4fe2-bcde-01d60fd046bb',
    'DROP_train_history_2450_7070d57e-bc9e-4892-b4c9-a8d94db5375c',
    'DROP_train_history_2450_798d4961-c561-421c-beca-9ea831bb7078',
    'DROP_train_history_2450_cbf3da23-7497-468c-bfb8-a5fbb3df2129',
    'DROP_train_history_2450_daa5a2be-cc66-46d2-ab80-7f777f007616',
    'DROP_train_history_2450_fba42a3e-bed7-4b1a-8df0-ea7de82314eb',
    'DROP_train_history_2451_17d93c83-e4ab-4e16-bba2-c99f9e8e5cd6',
    'DROP_train_history_2457_2acf50a6-df42-49b4-a20b-e4788475232d',
    'DROP_train_history_2458_75139a24-49df-4ce1-9d92-9e8528d020aa',
    'DROP_train_history_2463_3e736c0e-21d5-4503-bd70-24439a020956',
    'DROP_train_history_2467_4fcd1e63-5a95-4236-a435-c7265d75a7a4',
    'DROP_train_history_2467_63cddfc2-2a13-453b-8531-54b7608cb50b',
    'DROP_train_history_2472_e2cd90d3-ee33-4db1-bfec-298abe4c9724',
    'DROP_train_history_2481_1a7ae4ee-8a4b-47a8-b969-079062b1f53c',
    'DROP_train_history_2498_100d310a-52e3-4407-b171-51f53629ba10',
    'DROP_train_history_2514_7113b939-56e1-45d4-8910-f7d43012c8f0',
    'DROP_train_history_2541_61c9bbdb-1e1f-4321-9cc7-0a98b3c2af4e',
    'DROP_train_history_2583_e0a00e0c-f69d-4887-9bb4-33705ec5f947',
    'DROP_train_history_259_fef2cf95-7cca-4270-8a18-2823c3d71bba',
    'DROP_train_history_2592_08f95e84-752e-44ee-902d-d34bc6de0884',
    'DROP_train_history_2596_cda9b65b-21c6-46a5-ba85-0569f7b8e366',
    'DROP_train_history_2606_c4b8fa31-3e85-4eba-a941-cc94377eee33',
    'DROP_train_history_2630_50afb751-d3c0-4fcc-99bb-ce3bde8a84e6',
    'DROP_train_history_2648_d8573f9b-1625-47aa-9c28-b60c32d9184b',
    'DROP_train_history_2674_9b99eda6-31dd-4a3c-b959-a3e016183f35',
    'DROP_train_history_2684_fcf03aa4-9d7f-44ef-b37f-b81fa38783c2',
    'DROP_train_history_2702_6d777f36-11cc-4942-8a1a-c6e0f6c62170',
    'DROP_train_history_279_dbcc6dca-ed69-4a2a-aea4-bb8ffef7d77c',
    'DROP_train_history_2851_2e8afe13-1ef5-40c4-b045-24433913370b',
    'DROP_train_history_2853_5950e633-5ae1-414f-84e8-57b7585f480c',
    'DROP_train_history_2853_e9fc9201-a4af-49be-a31e-b55ed4d7d1ba',
    'DROP_train_history_2863_48dd44e2-8f6b-4228-bf01-ffe05ffba613',
    'DROP_train_history_2896_c2f5a28e-710d-418d-be26-ad8156e4e0df',
    'DROP_train_history_2902_28802121-fd4f-4a68-a4c8-d298ec4a0ce5',
    'DROP_train_history_2902_3c6c6118-f485-4298-99fc-08aeceac87e5',
    'DROP_train_history_2918_a6cbbe12-602d-4421-8531-1505aa46dce3',
    'DROP_train_history_292_3a845d0c-de0a-4cb1-8489-3c272af922a1',
    'DROP_train_history_2973_db6718a9-bbe2-4b9f-ac52-9edd8e5646ef',
    'DROP_train_history_3108_f61dadd7-ee21-4f39-b6f8-44ad1990cd99',
    'DROP_train_history_3112_4c7f18f6-8ca2-4f34-aa93-cfefc450b9cc',
    'DROP_train_history_3124_5f87f92b-9f4d-418b-b7f5-9042259b7067',
    'DROP_train_history_3124_7c6e619a-9bf8-43b2-b2e0-359c6ef4fa8a',
    'DROP_train_history_3186_a603f95b-b13e-484b-aa52-2e38f6e11d21',
    'DROP_train_history_3199_01083d8f-ed67-444c-927f-c0343a459c9e',
    'DROP_train_history_3218_df468eab-ae31-458b-a9fb-815a5b51d644',
    'DROP_train_history_3281_79ef8d0c-c239-4272-ab5e-0a9c28edaaa9',
    'DROP_train_history_3281_83417064-d6f7-447d-9402-c89b74673b1f',
    'DROP_train_history_3281_d6d374a1-1a1b-4feb-a01d-16a2a9264c66',
    'DROP_train_history_3281_ebe20cda-f0d9-4229-a426-320dbf6cef5f',
    'DROP_train_history_3324_14da331b-af95-4268-bb1b-4df7041a4c2e',
    'DROP_train_history_3398_646f3205-6b5f-4c58-b48e-7a814de29701',
    'DROP_train_history_3398_a9917964-bff6-4b74-a595-21dcf783fda4',
    'DROP_train_history_3398_ad0d1261-5025-45d6-a1f7-7a9cd5919b75',
    'DROP_train_history_3434_0656291e-089c-4639-babe-1b961899b4e9',
    'DROP_train_history_3434_a7a47c7e-eb2d-4465-9f53-fbf1a5758d21',
    'DROP_train_history_3436_bebd26c3-10b0-4075-ba79-33abc15709c7',
    'DROP_train_history_3546_0554cece-31aa-404b-bcd7-ca1415decc66',
    'DROP_train_history_3546_50b54e5b-4174-46a6-8c11-cb4a887e5be5',
    'DROP_train_history_3620_112de847-b15b-4615-b736-f2596a47360d',
    'DROP_train_history_3681_42a25c41-ff91-4ed5-9662-c80771387b73',
    'DROP_train_history_4129_de58689b-5f4b-42a5-9459-e41e1ba2d295',
    'DROP_train_history_464_3c170843-dacf-4c2f-8927-edbe7f58b801',
    'DROP_train_history_464_8e941c7d-454a-426a-95d8-add1676631f1',
    'DROP_train_history_500_317ae505-7c69-4872-a17c-dc86ae48aedb',
    'DROP_train_history_500_db82275d-38ce-42f5-a4d6-23dc8db231d2',
    'DROP_train_history_313_dacf32e9-8039-4d9c-8cf1-28a67eddfbac',
    'DROP_train_history_541_5d330e7f-74c5-4ab2-aa0b-ddf39030cf4d',
    'DROP_train_history_648_0f3190d6-687d-415c-9ec6-1753323a7556',
    'DROP_train_history_648_18f675c1-cd86-4a47-9ac8-6f0169b4cfc6',
    'DROP_train_history_718_37c1ee96-c2f9-41bf-a745-e95f2e6e0ba1',
    'DROP_train_history_731_1acef0a5-6400-4934-85d4-9817d88bcd12',
    'DROP_train_history_744_3b73177f-950b-483c-9291-67cbe93b3fe7',
    'DROP_train_history_981_a993f01e-b95f-486e-a5ac-9a6c69e99aa7',
    'DROP_train_nfl_338_8de196b9-3382-4276-89dd-8403c1fd76c1',
    'DROP_train_nfl_804_05d55c23-2fd2-4446-b3a6-66ac4fc7bd8f',
    'DROP_train_nfl_338_8de196b9-3382-4276-89dd-8403c1fd76c1',
    'DROP_train_nfl_804_05d55c23-2fd2-4446-b3a6-66ac4fc7bd8f',

    'SPIDER_train_2035',
    'SPIDER_train_2990',
    'SPIDER_train_3002',
    'SPIDER_train_3110',

    # Dev set:
    'CLEVR_dev_104',
    'CLEVR_dev_1918',
    'CLEVR_dev_5721',
    'CWQ_dev_WebQTest-1441_37d68ad3c2720a3fccdabd4e33f3bfbd',
    'DROP_dev_history_1167_04413034-93b3-4988-a9d0-a9ac74c2dd7d',
    'DROP_dev_history_1258_0711bebd-38ac-482f-878e-1f5aa9382897',
    'DROP_dev_history_1450_684416af-6cbf-44ee-8fd8-82c1a4f887f3',
    'DROP_dev_history_1731_65b66a61-6eb9-43e8-b245-8dd333be4fa3',
    'DROP_dev_history_1731_a28d736c-4b32-44f3-b24a-987775399f4f',
    'DROP_dev_history_1773_947307cd-6428-44c1-af51-55a7d2802496',
    'DROP_dev_history_1773_c2b99dcd-f6a3-4928-ac83-8a88518e7fc1',
    'DROP_dev_history_1802_b0840ae1-87f7-4396-b8d1-2661d91bd9a5',
    'DROP_dev_history_1859_7c7aeed2-3f87-483a-824b-c8bd10d576f8',
    'DROP_dev_history_1859_7dd6cc9c-8344-46f0-a63d-a4d73414753b',
    'DROP_dev_history_1860_354675ed-a147-4b07-b41c-78c6cbdc9b82',
    'DROP_dev_history_1860_435cd2ca-6dea-4957-9642-d79ac09cb712',
    'DROP_dev_history_1860_695eb057-cd16-43b6-ae10-642117235f62',
    'DROP_dev_history_1863_b73c649b-7d9e-433b-8ac0-c91de4b48a6c',
    'DROP_dev_history_1876_a0e4aa81-3902-487b-a6c1-7f406a15aa27',
    'DROP_dev_history_1884_7944e5b2-d3c2-4eaf-9a58-91fef27335e7',
    'DROP_dev_history_1884_79cca8c7-6300-42d8-a594-6757ee3d19b0',
    'DROP_dev_history_1892_60de0e6e-4f2a-4522-850e-e5d83555e7cb',
    'DROP_dev_history_1892_8c2c294d-c471-4da0-9631-ecc13b6b4ebd',
    'DROP_dev_history_1892_ec48ffdd-f2c8-4c2b-9098-11264d5f614f',
    'DROP_dev_history_1898_421eb770-cd50-489c-9c1c-f10688c05c3b',
    'DROP_dev_history_1898_421eb770-cd50-489c-9c1c-f10688c05c3b',
    'DROP_dev_history_1935_72993c31-5d42-4d25-a1e2-2814b3e8bc8b',
    'DROP_dev_history_1935_abeebbf2-bf81-47bb-940f-7317ff58b8a3',
    'DROP_dev_history_1935_bf12abdc-0a53-4a6f-ada5-158af4206ea2',
    'DROP_dev_history_1935_ec91e815-70ef-4614-8c12-7c3ac580f1d2',
    'DROP_dev_history_1940_4c1b0cdf-242a-4d51-a71e-20730bbf23c6',
    'DROP_dev_history_1940_e5186d1f-b011-48ed-a61d-8e79b0fdee5e',
    'DROP_dev_history_1948_8cb2008f-f407-41c4-9eb6-1e796bcb4278',
    'DROP_dev_history_1954_7af25553-830e-4dc5-a406-5031ecc79150',
    'DROP_dev_history_1959_b510bfa4-0657-4787-9881-eb26c4411d88',
    'DROP_dev_history_2014_67f5f3fe-f418-486f-9a36-6ca00451f5a0',
    'DROP_dev_history_2014_6803b732-55bf-4412-9b4a-642f30e7cecf',
    'DROP_dev_history_2014_b6b2a97f-f496-454f-bfb6-376847bf151c',
    'DROP_dev_history_2088_3daad9bd-055b-4c19-a5b2-f360ee1fb638',
    'DROP_dev_history_2142_064ea513-bf9b-46bd-bcdd-1f221dabad9a',
    'DROP_dev_history_2142_373f73fb-83ea-483f-a7c3-1cbed017ad84',
    'DROP_dev_history_2162_96171ae9-6096-4b1b-a2b3-88f25f75989b',
    'DROP_dev_history_2162_9e860e5c-a113-41b4-b609-b1b6223727cf',
    'DROP_dev_history_2162_af33339f-91ba-46c8-bf69-cd5aea8c8b71',
    'DROP_dev_history_2170_467dc327-60ca-41b2-9eb1-945518b72edc',
    'DROP_dev_history_2170_749ed05c-22fc-4ba8-ac83-040be66718d5',
    'DROP_dev_history_2187_27189445-ef12-49b8-8cdb-d1e2f79799c5',
    'DROP_dev_history_2187_32a8d1bc-8cba-4f9c-b219-43ac7d12b831',
    'DROP_dev_history_2187_9cfda451-d4d6-4191-bd43-ee0f38711cb5',
    'DROP_dev_history_2188_399d1a7c-eebd-4fbf-8110-37d74032bab3',
    'DROP_dev_history_2188_420c9197-ccfb-4354-8f62-0f9ea5282d17',
    'DROP_dev_history_2196_4c3a97cc-6c26-480c-b555-de4c53fda310',
    'DROP_dev_history_2196_5ff917c0-8ebc-4b03-baad-4deee565b508',
    'DROP_dev_history_2196_69ef3d8a-bbb7-462f-9519-ff32941b51da',
    'DROP_dev_history_2196_c91c3b0f-c77c-41f9-bd9a-d5cc0e897783',
    'DROP_dev_history_2196_f09257e6-b661-4e27-90fa-71e2915f1eda',
    'DROP_dev_history_254_e8caaba6-6e7c-4170-af2c-f2faf35154ff',
    'DROP_dev_history_2626_1b9e0b8b-9075-467d-b249-e34e28f09f05',
]


def is_noisy_data(target, operations, question_id):
    # this is not a regular QDMR, we'll drop this data.
    return 'None' in operations or question_id in DATA_BLACKLIST
