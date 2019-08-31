unit FmxInvalidateHack;

interface

uses
  Fmx.Types, Vcl.Controls;

procedure InvalidateControl(aControl : TControl);


implementation

uses
  Contnrs;

type
  TInvalidator = class
  private
  protected
    Timer : TTimer;
    List  : TObjectList;
    procedure Step(Sender : TObject);
  public
    constructor Create;
    destructor Destroy; override;

    procedure AddToQueue(aControl : TControl);
  end;

var
  GlobalInvalidator : TInvalidator;

procedure InvalidateControl(aControl : TControl);
begin
  if not assigned(GlobalInvalidator) then
  begin
    GlobalInvalidator := TInvalidator.Create;
  end;
  GlobalInvalidator.AddToQueue(aControl);
end;


{ TInvalidator }

constructor TInvalidator.Create;
const
  FrameRate = 30;
begin
  List  := TObjectList.Create;
  List.OwnsObjects := false;

  Timer := TTimer.Create(nil);
  Timer.OnTimer  := Step;
  Timer.Interval := round(1000 / FrameRate);
  Timer.Enabled  := true;
end;

destructor TInvalidator.Destroy;
begin
  Timer.Free;
  List.Free;
  inherited;
end;

procedure TInvalidator.AddToQueue(aControl: TControl);
begin
  if List.IndexOf(aControl) = -1 then
  begin
    List.Add(aControl);
  end;
end;

procedure TInvalidator.Step(Sender: TObject);
var
  c1: Integer;
begin
  for c1 := 0 to List.Count-1 do
  begin
    (List[c1] as TControl).Repaint;
  end;
  List.Clear;
end;


initialization

finalization
  if assigned(GlobalInvalidator) then GlobalInvalidator.Free;

end.
