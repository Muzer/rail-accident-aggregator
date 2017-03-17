import raa.accident as accident
import operator

def output(accidents):
    accidents.sort(key=lambda x : x.published.date())
    for accident in accidents:
        print(accident.desc)
        print("From " + accident.org + " in " + accident.country)
        print("Download " + accident.url)
        print("At " + str(accident.location))
        print("Details " + str(accident.longdesc))
        print("Occurred on " + str(accident.date))
        print("Published on " + str(accident.published))
        if accident.alturls and 'landing' in accident.alturls:
            print("More info: " + accident.alturls['landing'])
        print('\n\n')

