// Independent entity resolver candidate. Never override a shared campus address.
const aliases=new Set(['國立臺灣大學辛亥地下停車場','臺大辛亥地下停車場','辛亥地下停車場']);
export function resolveParkingEntity({query='',officialId=null}={}) {
 if(officialId && officialId!=='TPE0880') return null;
 if(!aliases.has(query.trim())) return null;
 return {officialId:'TPE0880',name:'國立臺灣大學辛亥地下停車場',lat:25.020797779252113,lon:121.54229620209323,precision:'parking-site-reference',entranceVerified:false,source:'https://map.ntu.edu.tw/index.html',sourceRecord:'TR022-C-01'};
}
