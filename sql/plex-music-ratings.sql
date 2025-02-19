select  i.id, mi.title, mp.file,  mis.rating,
                i.library_section_id||'-'||ls.name library_secion,
                i.section_location_id||'-'||sl.root_path section_location,
                i.metadata_item_id, mi.metadata_type , i.container
FROM    media_items i
join    metadata_items mi on i.metadata_item_id = mi.id
left outer join library_sections ls on i.library_section_id = ls.id
left outer join section_locations sl on i.section_location_id = sl.id
JOIN    media_parts mp on i.id = mp.media_item_id
join metadata_items mdi on i.metadata_item_id = mdi.id
LEFT OUTER JOIN metadata_item_settings mis on mdi.guid = mis.guid
where   mi.library_section_id  = 4
and     ( mis.rating is null or mis.rating = 0 )
order by i.size desc
;