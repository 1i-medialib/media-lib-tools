-- Plex Library File Sizes
select  i.id, mi.title, mp.file, i.size,
                i.library_section_id||'-'||ls.name library_secion,
                i.section_location_id||'-'||sl.root_path section_location,
                i.metadata_item_id, mi.metadata_type , i.container
FROM    media_items i
join    metadata_items mi on i.metadata_item_id = mi.id
left outer join library_sections ls on i.library_section_id = ls.id
left outer join section_locations sl on i.section_location_id = sl.id
JOIN    media_parts mp on i.id = mp.media_item_id
where i.library_section_id  is not NULL
order by i.size desc
;