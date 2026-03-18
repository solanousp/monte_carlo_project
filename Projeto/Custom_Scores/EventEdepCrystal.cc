// Scorer for EventEdepCrystal

#include "EventEdepCrystal.hh"

#include "TsExtensionManager.hh"
#include "TsParameterManager.hh"
#include "TsMaterialManager.hh"
#include "TsGeometryManager.hh"

#include "G4SystemOfUnits.hh"

EventEdepCrystal::EventEdepCrystal(TsParameterManager* pM,
                                   TsMaterialManager* mM,
                                   TsGeometryManager* gM,
                                   TsScoringManager* scM,
                                   TsExtensionManager* eM,
                                   G4String scorerName,
                                   G4String quantity,
                                   G4String outFileName,
                                   G4bool isSubScorer)
    : TsVNtupleScorer(pM, mM, gM, scM, eM, scorerName, quantity, outFileName, isSubScorer),
      fEventEdep(0.)
{
    fNtuple->RegisterColumnD(&fEventEdep, "EventEdep", "MeV");
}

EventEdepCrystal::~EventEdepCrystal()
{
}

G4bool EventEdepCrystal::ProcessHits(G4Step* aStep, G4TouchableHistory*)
{
    G4double edep = aStep->GetTotalEnergyDeposit();

    if (edep > 0.)
        fEventEdep += edep / MeV;

    return true;
}

void EventEdepCrystal::UserHookForEndOfEvent()
{
    fNtuple->Fill();
    fEventEdep = 0.;
}
