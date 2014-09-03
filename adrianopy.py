# Adriano's Python solution

# separate the ivestigator id into a new table
names = pd.Series(["Grant.Application.ID", "Person.ID", "Role", "Year.of.Birth", "Country.of.Birth", "Home.Language", "Dept.No.", "Faculty.No.","With.PHD", "No..of.Years.in.Uni.at.Time.of.Grant", "Number.of.Successful.Grant", "Number.of.Unsuccessful.Grant", "A.", "A", "B", "C"])
col = pd.Series(["Grant.Application.ID", "Person.ID.%d", "Role.%d", "Year.of.Birth.%d", "Country.of.Birth.%d", "Home.Language.%d", "Dept.No..%d", "Faculty.No..%d","With.PHD.%d", "No..of.Years.in.Uni.at.Time.of.Grant.%d", "Number.of.Successful.Grant.%d", "Number.of.Unsuccessful.Grant.%d", "A..%d", "A.%d", "B.%d", "C.%d"])
invest = pd.DataFrame(columns=names)
for i in range(1,16):
    # create columns name
    a = df[col.apply(lambda x: x %i if('%' in x) else x)]
    a.columns = names
    #valid = a[a['Person.ID']>0]
    valid = a.dropna(subset=['three', 'four', 'five'], how='all')
    invest = pd.concat([invest,valid])
invest.shape
print 'Unique person ID %d' %len(invest["Person.ID"].unique())
print 'Unique records {}'.format(invest.drop_duplicates().shape)
invest = invest.drop_duplicates()
final_data = df[df.columns[1:26]]
final_data.join(invest)