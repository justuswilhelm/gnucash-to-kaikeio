select accounts.guid
, accounts.code
, accounts.name
, parent_accounts.name as parent_name
, parent_accounts.code as parent_code
from accounts inner join accounts as parent_accounts on accounts.parent_guid = parent_accounts.guid;
