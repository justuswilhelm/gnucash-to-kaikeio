select accounts.guid
, case parent_accounts.code
    when '' then accounts.code
    else parent_accounts.code
    end as code
, case parent_accounts.code
    when '' then accounts.name
    else parent_accounts.name
    end as name
, case parent_accounts.code
    when '' then null
    else accounts.code
    end as supplementary_code
, case parent_accounts.code
    when '' then null
    else accounts.name
    end as supplementary_name
from accounts
inner join accounts as parent_accounts on accounts.parent_guid = parent_accounts.guid
