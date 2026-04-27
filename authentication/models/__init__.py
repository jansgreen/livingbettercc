from .profiles import AcademicEvidence, Profiles, ScholarshipStudentInfo
from .customers import Customers
from .students import Students
from .staffs import Staffs
from .directives import Directives

# Nota: "Address" ahora vive en la app anidada "authentication.address".
# Evitamos reexportarlo desde authentication.models para prevenir conflictos.
