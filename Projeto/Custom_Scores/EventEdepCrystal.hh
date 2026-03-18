#ifndef EventEdepCrystal_hh
#define EventEdepCrystal_hh

#include "TsVNtupleScorer.hh"
#include "G4Step.hh"

class TsExtensionManager;

class EventEdepCrystal : public TsVNtupleScorer
{
public:
    EventEdepCrystal(TsParameterManager* pM,
                     TsMaterialManager* mM,
                     TsGeometryManager* gM,
                     TsScoringManager* scM,
                     TsExtensionManager* eM,
                     G4String scorerName,
                     G4String quantity,
                     G4String outFileName,
                     G4bool isSubScorer);

    virtual ~EventEdepCrystal();

    G4bool ProcessHits(G4Step*, G4TouchableHistory*) override;
    void UserHookForEndOfEvent() override;

private:
    G4double fEventEdep;
};

#endif
