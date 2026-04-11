from output.report_builder import build_triage_report, print_report, save_report

messages = [
    # Urgent complaint
    "Hi, I'm Priya Sharma. The ceiling in my flat APT-2047 in Bandra West "
    "is leaking badly and furniture is getting damaged. "
    "Please send someone by 15th April. My number is 9876543210.",

    # Medium booking
    "I'd like to schedule a property viewing for Unit B-12 in Powai "
    "on 20th April at 11am. Please confirm. - Rahul Mehta, 9123456780",

    # Low query
    "Can you tell me what documents are needed for renting a 2BHK flat?",
]

for i, msg in enumerate(messages, 1):
    print(f"\n\n{'🧪 TEST ' + str(i) + ' ':{'═'}<60}")

    report = build_triage_report(msg)   # build
    print_report(report)                # display
    save_report(report)                 # save to /output/reports/


