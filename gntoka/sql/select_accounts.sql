select accounts.guid
, case parent_accounts.placeholder
    when 1 then accounts.code
    else parent_accounts.code
    end as code
, case parent_accounts.placeholder
    when 1 then accounts.name
    else parent_accounts.name
    end as name
, case parent_accounts.placeholder
    when 1 then null
    else accounts.code
    end as supplementary_code
, case parent_accounts.placeholder
    when 1 then null
    else accounts.name
    end as supplementary_name
from accounts
inner join (
    select guid
    , code
    , name
    , placeholder
    from accounts
)
as parent_accounts on accounts.parent_guid = parent_accounts.guid
where accounts.placeholder = 0
