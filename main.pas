unit main;

interface

uses
  System.SysUtils, System.Types, System.UITypes, System.Classes, System.Variants,
  FMX.Types,FMX.Memo.Types,FMX.Platform.Win,FMX.Controls, FMX.Forms, FMX.Graphics, FMX.Dialogs, FMX.Objects, FMX.Layouts,Windows,Messages, FMX.StdCtrls, FMX.Effects,
  FMX.Ani, System.Math.Vectors, FMX.Controls3D, FMX.Layers3D, FMX.Viewport3D, FMX.Controls.Presentation, FMX.ListBox, FMX.TreeView, FMX.Edit,
  System.Threading,IOUtils, FMX.Colors, FMX.ScrollBox, FMX.Memo, SyncObjs,XMLDoc, xmldom, XMLIntf;


  type TMyPseudoThreadPoolKurkulator = class(TObject)
    constructor Create(Files : TArray<System.string>);  overload;
    destructor  Destroy;
    public
     procedure DoKurkulate(oResult:TStrings; ProgressBar:Tline; XMLSavePath:string);
    private
     myFiles: TArray<System.string>;
    end;

type
  TMForm = class(TForm)
    topl: TLayout;
    toplr: TRectangle;
    mlayout: TLayout;
    sgrip: TSizeGrip;
    MRect: TRectangle;
    GE: TGlowEffect;
    startAnim: TFloatAnimation;
    logoLayout: TLayout;
    logoImg: TImage;
    logoImg0: TImage;
    logoxanim: TFloatAnimation;
    logo0xanim: TFloatAnimation;
    toplanim: TFloatAnimation;
    closeBtn: TImage;
    canim: TColorAnimation;
    blure: TBlurEffect;
    MRectLayout: TLayout;
    editPath: TEdit;
    FolderBttn: TButton;
    Image1: TImage;
    splitLine: TLine;
    runBttn: TButton;
    runInfoLabel: TLabel;
    runRect: TRectangle;
    progressLine: TLine;
    findAnim: TFloatAnimation;
    memoLog: TMemo;
    splitLine0: TLine;
    progressLine0: TLine;
    pregressLine1: TLine;
    procedure toplrMouseDown(Sender: TObject; Button: TMouseButton; Shift: TShiftState; X, Y: Single);
    procedure startAnimProcess(Sender: TObject);

    procedure startAnimFinish(Sender: TObject);
    procedure logoxanimFinish(Sender: TObject);
    procedure logo0xanimFinish(Sender: TObject);
    procedure toplanimProcess(Sender: TObject);
    procedure toplanimFinish(Sender: TObject);
    procedure closeBtnMouseEnter(Sender: TObject);
    procedure closeBtnMouseLeave(Sender: TObject);
    procedure closeBtnClick(Sender: TObject);
    procedure FolderBttnClick(Sender: TObject);
    procedure sgripKeyUp(Sender: TObject; var Key: Word; var KeyChar: Char; Shift: TShiftState);
    procedure findAnimProcess(Sender: TObject);
    procedure runBttnClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure MRectLayoutPaint(Sender: TObject; Canvas: TCanvas; const ARect: TRectF);
    procedure memoLogChange(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  MForm: TMForm;
  Files,Dirs : TArray<System.string>;
  Kurkulator : TMyPseudoThreadPoolKurkulator;
  KCounter   : Integer = 0; // счётчик выполененных заданий в потоках
  T: TDateTime;

implementation

{$R *.fmx}

procedure TMForm.closeBtnClick(Sender: TObject);
begin
Close;
end;

{$REGION 'Анимация кнопки закрытия окна'}
procedure TMForm.closeBtnMouseEnter(Sender: TObject);
begin
 TImage(Sender).Opacity:= 0.5;
end;

procedure TMForm.closeBtnMouseLeave(Sender: TObject);
begin
 TImage(Sender).Opacity:= 1.0;
end;
procedure TMForm.findAnimProcess(Sender: TObject);
begin
  blure.UpdateParentEffects;
end;

{$ENDREGION}

// Нажатие кнопки выбора папки
procedure TMForm.FolderBttnClick(Sender: TObject);
var path:string;
  i: Integer;
begin

memoLog.Lines.Clear;
//blure.Enabled := false;

// Очистка памяти
 if Length(Files)>0 then
 begin
   for i:=0 to Length(Dirs)-1 do Dirs[i]:='';
 end;
  if Length(Files)>0 then
 begin
   for i:=0 to Length(Files)-1 do Files[i]:='';
 end;

 SelectDirectory('Select folder', path, path);

  editPath.Text := path;
  editPath.Enabled := true;


 // поиск в отдельном потоке, чтобы не зависл иннтерфес
 // запускается анимация для отображения процесс поиска
 //  progressLine.Visible:= true;  -- временно выпилил, так как есть непотные глюки

 runInfoLabel.Text := '-';
 TTask.run
 (
 procedure
 var i:integer;
 begin
   Files := TDirectory.GetFiles(path, '*.*', TSearchOption.soAllDirectories);
   Dirs  := TDirectory.GetDirectories(path,'*',  TSearchOption.soAllDirectories);
   runInfoLabel.Text := length(Files).ToString + ' files and ' + length(Dirs).ToString + ' folders found';
  // blure.UpdateParentEffects;
   for i:=0 to Length(Files) do
   begin
    memoLog.Lines.Add('  '+Files[i]);
    memoLog.RecalcUpdateRect;
    memoLog.GoToTextEnd;     // проматываю в конец списка
    MForm.memoLog.UpdateContentSize;
    MForm.memoLog.UpdateEffects;
    sleep(10);
   end;

 end
  );

end;

procedure TMForm.FormCreate(Sender: TObject);
begin
 MRectLayout.Visible:= false;
 blure.Enabled := true;
 logoLayout.Visible := true;
 topl.Height := 0.01;
 logoImg.Position.X := -400;
 logoImg0.Position.X := 750;
 findAnim.StopValue := splitLine.Width-progressLine.Width; // получаю коенечную позицию линии для анимации поиска файлов

 TTAsk.Run(
 procedure
 begin
  while true do
  begin
    if blure.Enabled then blure.UpdateParentEffects;
    sleep(500);
  end;
 end
 );

end;

procedure TMForm.logo0xanimFinish(Sender: TObject);
begin
toplanim.Enabled := true;
end;

procedure TMForm.logoxanimFinish(Sender: TObject);
begin
logo0xanim.Enabled := true;
end;

procedure TMForm.memoLogChange(Sender: TObject);
begin
memoLog.ScrollTo(0,5);
end;

procedure TMForm.MRectLayoutPaint(Sender: TObject; Canvas: TCanvas; const ARect: TRectF);
begin
blure.UpdateParentEffects;
end;

procedure TMForm.runBttnClick(Sender: TObject);
var Pooool : TThreadPool;

begin
 T := Time;
 memoLog.Lines.Clear;
 memoLog.Lines.Add(#13#10+'             Kurkulation started :: '+ TimeToStr(T) +#13#10) ;
 Kurkulator := TMyPseudoThreadPoolKurkulator.Create(Files);
 TTask.run(
 procedure
 begin
  Kurkulator.DoKurkulate(memoLog.Lines, progressLine0, editPath.Text);
 end
 );
end;

procedure TMForm.sgripKeyUp(Sender: TObject; var Key: Word; var KeyChar: Char; Shift: TShiftState);
begin
  findAnim.StopValue := splitLine.Width-progressLine.Width;
end;

procedure TMForm.startAnimFinish(Sender: TObject);
begin

mlayout.Enabled := true;
mlayout.Opacity := 1;
logoxanim.Enabled := true;
end;

procedure TMForm.startAnimProcess(Sender: TObject);
begin
GE.UpdateParentEffects;
end;

procedure TMForm.toplanimFinish(Sender: TObject);
begin
     MRectLayout.Visible:=true;
     topl.Height := 25;
end;

procedure TMForm.toplanimProcess(Sender: TObject);
begin
 sgrip.Opacity := sgrip.Opacity + 0.05;
 logoLayout.Opacity := logoLayout.Opacity - 0.1;
end;



procedure TMForm.toplrMouseDown(Sender: TObject; Button: TMouseButton; Shift: TShiftState; X, Y: Single);
 var
  hw : HWND;
begin
 hw := FindWindow(nil,PChar(MForm.Caption));
 ReleaseCapture;
 SendMessage(hw, WM_SysCommand,61458,0);
end;

{ TMyPseudoThreadPoolCalculator }

destructor TMyPseudoThreadPoolKurkulator.Destroy;
 var i:integer;
begin
Inherited Destroy;
 for i:=0 to Length(myFiles)-1 do myFiles[i]:='';
end;

procedure TMyPseudoThreadPoolKurkulator.DoKurkulate(oResult:TStrings; ProgressBar:Tline;XMLSavePath:string);
var
    pbv: single;
    sumArray : TArray<Int64>;
  XML : IXMLDOCUMENT;
  RootNode, CurNode, PrevNode : IXMLNODE;
  k: Integer;
begin

 KCounter := 0;
 ProgressBar.Visible := True;
 ProgressBar.Width := 0;
 pbv := TLine(ProgressBar.Parent).Width/Length(myFiles);
 TParallel.For(0,length(myFiles)-1,
 procedure (i:integer)
 var
   fs: TFileStream;
    j: Int64;
  sum: Int64;
  buf: Byte;
 begin
  fs := TFileStream.Create(myFiles[i],fmOpenRead);
  SetLength(sumArray,length(myFiles));
  for j := 0 to fs.Size do
  begin
   fs.Seek(j,soFromBeginning);  //перемещаюсь по файлу
   fs.Read(buf,1);              // читаю бит по смещению
   sum := sum + buf;            // суммирую
  end;
   TInterlocked.Increment(KCounter); // подсчёт выполенных задач
   sumArray[i] := sum;
   oResult.Append('  ' + ExtractFileName(myFiles[i]) + ' -> Kurkulated Sum :: ' + sum.ToString +' | ' + KCounter.ToString + ' of ' + length(myFiles).ToString);
   ProgressBar.Width := ProgressBar.Width + pbv;   // индикация процесса вычисления
    MForm.memoLog.GoToTextEnd;
    MForm.memoLog.UpdateContentSize;
    MForm.memoLog.UpdateEffects;
   if KCounter = Length(myFiles) then     // если последее задание, то вывожу сообщение об окончании
   begin
    T := Time;
    oResult.Append(#13#10+'             Kurkulation completed :: '+ TimeToStr(T) +#13#10) ;

    oResult.Append(#13#10+'             '+PChar(XMLSavePath+'\Kurkulator.xml') +#13#10) ;

    sleep(10);
    MForm.memoLog.ScrollBy(MForm.memoLog.Lines.Count,0);
    MForm.memoLog.GoToTextEnd;
    MForm.memoLog.UpdateContentSize;
    MForm.memoLog.UpdateEffects;
   end;



   sum := 0;
   fs.Free;
 end
 );


  XML := TXMLDocument.Create(nil);
  XML.Active := true;
  XML.Options := [doNodeAutoIndent];
  XML.Encoding := 'utf-8';
  XML.DocumentElement := XML.CreateNode('KurkulatorXML',ntElement);

  for k := 0 to Length(myFiles)-1 do
  begin
   CurNode := XML.DocumentElement.AddChild('File'+k.ToString);
   PrevNode:= CurNode;
   CurNode := CurNode.AddChild('Path');
   CurNode.Text := myFiles[k];
   PrevNode := PrevNode.AddChild('Sum');
   PrevNode.Text := sumArray[k].ToString;
  end;

     XML.SaveToFile( PChar(XMLSavePath+'\Kurkulator.xml'));
     FreeAndNil(XML);
     FreeAndNil(Kurkulator);

end;

constructor TMyPseudoThreadPoolKurkulator.Create(Files : TArray<System.string>);
begin
Inherited Create();
  myFiles := Files;
end;

end.
